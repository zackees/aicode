"""aicode - front end for aider"""

import argparse
import atexit
import os
import shutil
import subprocess
import sys
import time
import warnings
from dataclasses import dataclass
from pathlib import Path
from threading import Thread
from typing import Optional, Tuple, Union

from aicode.openaicfg import create_or_load_config, save_config
from aicode.util import aider_fetch_update_string_if_out_of_date, extract_version_string

CHAT_GPT = "openai/gpt-4o"


@dataclass
class Model:
    name: str
    description: str
    model_str: str


MODELS = {
    "chatgpt": Model("gpt-4o", "The GPT-4o model.", CHAT_GPT),
    "claude": Model("claude", "The Claude model.", "sonnet"),
}

CLAUD3_MODELS = {"claude"}

MODEL_CHOICES = list(MODELS.keys())


def install_aider_if_missing() -> None:
    bin_path = os.path.expanduser("~/.local/bin")
    os.environ["PATH"] = os.environ["PATH"] + os.pathsep + bin_path
    if shutil.which("aider") is not None:
        return
    print("Installing aider...")
    rtn = os.system("pipx install aider-chat")
    if rtn != 0:
        assert False, "Failed to install aider"
    assert shutil.which("aider") is not None, "aider not found after install"


class CustomHelpParser(argparse.ArgumentParser):
    def print_help(self):
        # Call the default help message
        super().print_help()
        # Add additional help from the tool you're wrapping
        # print("\n Print aider --help:")

        aider_installed = shutil.which("aider") is not None
        if not aider_installed:
            print("aider is not installed, no more help available.")
            sys.exit(0)
        # aider_config = os.path.exists(".aider.conf.yml")
        # if not aider_config:
        #     print("\naider config file not found, no more help available.")
        #     sys.exit(1)
        print("\n\n############ aider --help ############")
        completed_proc = subprocess.run(
            ["aider", "--help"], check=False, capture_output=True
        )
        stdout = completed_proc.stdout.decode("utf-8")
        print(stdout)
        sys.exit(0)
        # make sure and return exit 0 on help message.


def parse_args() -> Tuple[argparse.Namespace, list]:
    argparser = CustomHelpParser(
        usage=(
            "Ask OpenAI for help with code, uses aider-chat on the backend."
            " Any args not listed here are assumed to be for aider and will be passed on to it."
        )
    )
    argparser.add_argument(
        "prompt", nargs="*", help="Args to pass onto aider"
    )  # Changed nargs to '*'
    argparser.add_argument("--set-key", help="Set OpenAI key")
    argparser.add_argument("--set-anthropic-key", help="Set Claude key")
    argparser.add_argument(
        "--upgrade", action="store_true", help="Upgrade aider using pipx"
    )
    argparser.add_argument(
        "--keep", action="store_true", help="Keep chat/input history"
    )
    argparser.add_argument(
        "--auto-commit",
        "-a",
        action="store_true",
    )
    model_group = argparser.add_mutually_exclusive_group()

    model_group.add_argument(
        "--claude",
        action="store_true",
    )
    model_group.add_argument("--model", choices=MODEL_CHOICES, help="Model to use")
    model_group.add_argument(
        "--chatgpt",
        action="store_true",
        help="Use ChatGPT model",
    )
    args, unknown_args = argparser.parse_known_args()

    return args, unknown_args


def cleanup() -> None:
    files = [
        ".aider.chat.history.md",
        ".aider.input.history",
    ]
    for file in files:
        if os.path.exists(file):
            try:
                os.remove(file)
            except OSError:
                warnings.warn(f"Failed to remove {file}")


def upgrade_aider() -> None:
    print("Upgrading aider...")
    rtn = os.system("pipx upgrade aider-chat")
    if rtn == 0:
        print("Upgrade successful.")
        return
    warnings.warn("Upgrade failed, pipx may be out of date.")
    yes = input("Would you like to try upgrading pipx? [y/N] ")
    if yes.lower() != "y":
        return
    print("Upgrading pipx...")
    PYTHON_EXE = sys.executable
    rtn = os.system(f'"{PYTHON_EXE}" -m pip install --upgrade pipx')
    if rtn != 0:
        warnings.warn("Failed to upgrade pipx.")
        return
    rtn = os.system("pipx install aider-chat")
    if rtn == 0:
        print("Reinstall successful.")
        return
    warnings.warn("Failed to upgrade aider.")


def get_model(
    args: argparse.Namespace, anthropic_key: Optional[str], openai_key: Optional[str]
) -> str:
    if args.claude:
        assert "claude" in MODELS
        return "claude"
    elif args.chatgpt:
        return CHAT_GPT
    elif args.model is not None:
        return args.model
    elif anthropic_key is not None:
        return "claude"
    elif openai_key is not None:
        return CHAT_GPT
    return "claude"


@dataclass
class AiderUpdateResult:
    has_update: bool
    latest_version: str
    current_version: str
    error: Optional[str] = None

    def get_update_msg(self) -> str:
        msg = "\n#######################################\n"
        msg += f"# UPDATE AVAILABLE: {self.current_version} -> {self.latest_version}.\n"
        msg += "# run `aicode --upgrade` to upgrade\n"
        msg += "#######################################\n"
        return msg

    def to_json_data(self) -> dict[str, Union[str, bool, None]]:
        return {
            "has_update": self.has_update,
            "latest_version": self.latest_version,
            "current_version": self.current_version,
            "error": str(self.error) if self.error is not None else None,
        }

    @classmethod
    def from_json(cls, json_data: dict[str, Union[str, bool]]) -> "AiderUpdateResult":
        return AiderUpdateResult(
            has_update=bool(json_data["has_update"]),
            latest_version=str(json_data["latest_version"]),
            current_version=str(json_data["current_version"]),
            error=str(json_data["error"]) if json_data["error"] is not None else None,
        )


def aider_check_update(current_version: Optional[str]) -> AiderUpdateResult:
    new_update_version: str | None = None
    try:
        new_update_version = aider_fetch_update_string_if_out_of_date()
        if new_update_version is None:
            return AiderUpdateResult(False, "", "")
    except KeyboardInterrupt:
        raise
    except Exception:  # pylint: disable=broad-except
        return AiderUpdateResult(False, "", "")
    if current_version is None:
        cmd = "aider --version"
        stdout = subprocess.run(cmd, capture_output=True, check=False, text=True).stdout
        stdout = stdout.strip()
        try:
            current_version = extract_version_string(stdout)
        except Exception:
            warnings.warn(f"Could not extract version info from {stdout}")
            current_version = "Unknown"
    try:
        latest_version: str = extract_version_string(new_update_version)
        has_update = latest_version != current_version
        out = AiderUpdateResult(has_update, latest_version, current_version)
        return out
    except Exception as err:  # pylint: disable=broad-except
        warnings.warn(f"Failed to parse update message: {stdout}\n because of {err}")
        pass
    return AiderUpdateResult(True, "Unknown", current_version)


def check_gitignore() -> None:
    needles: dict[str, bool] = {
        ".aider*": False,
        "!.aider.conf.yml": False,
        "!.aiderignore": False,
    }
    if os.path.exists(".gitignore"):
        any_missing = False
        with open(".gitignore", encoding="utf-8", mode="r") as file:
            content = file.read()
            lines = content.split("\n")
            for needle in needles:
                if needle in lines:
                    needles[needle] = True
                else:
                    any_missing = True
                    print(f".gitignore file does not contain {needle}")
        if any_missing:
            resp = input("Add them? [y/N] ")
            if resp.lower() == "y":
                with open(".gitignore", encoding="utf-8", mode="a") as file:
                    for needle, found in needles.items():
                        if not found:
                            file.write("\n" + needle)
    else:
        print(".gitignore file does not exist.")


def background_update_task(config: dict) -> None:
    try:
        # Wait for aider to start so that we don't impact startup time.
        # This is really needed for windows because startup is so slow.
        time.sleep(5)
        current_version = None
        aider_update_info = config.get("aider_update_info")
        if aider_update_info is not None:
            current_version = aider_update_info.get("current_version")
            if current_version == "Unknown":
                current_version = None
        update_info = aider_check_update(current_version)
        if update_info.has_update:
            config["aider_update_info"] = update_info.to_json_data()
            save_config(config)
        else:
            config["aider_update_info"] = {}
            save_config(config)
    except KeyboardInterrupt:
        pass
    except SystemExit:
        pass


def fix_escape_chars(path: str) -> str:
    if os.name != "nt":
        return path  # not necessary on posix systems
    if os.path.exists(path):
        return Path(path).as_posix()
    return path


def fix_paths(unknown_args: list) -> list:
    if os.name != "nt":
        # No path conversion needed on posix systems
        return unknown_args
    is_git_bash_or_cygwin = "MSYSTEM" in os.environ
    if not is_git_bash_or_cygwin:
        # No path conversion needed on windows cmd
        return unknown_args
    out: list = []
    for arg in unknown_args:
        try:
            arg_fixed = fix_escape_chars(arg)
            out.append(arg_fixed)
        except Exception:
            out.append(arg)
    return out


def check_aiderignore() -> None:
    """Adds the .aiderignore file if it doesn't exist."""
    if not os.path.exists(".aiderignore"):
        file_content = (
            "# Add files or directories to ignore here\n"
            "\n"
            "run\n"
            "lint\n"
            "test\n"
            "install\n"
            "clean\n"
        )
        with open(".aiderignore", encoding="utf-8", mode="w") as file:
            file.write(file_content)


def find_path_to_git_directory(cwd: Path) -> Path:
    path = cwd
    prev_path = None
    while path != Path("/"):
        if (path / ".git").exists():
            return path
        prev_path = path
        path = path.parent
        if path == prev_path:
            break
    raise FileNotFoundError("No git directory found")


def cli() -> int:
    # does .git directory exist?
    try:
        cwd = Path.cwd()
        path = find_path_to_git_directory(cwd=cwd)
        print("Found git directory at", path)
        os.chdir(str(path))
    except FileNotFoundError:
        print(f"There is no git directory at or above the current directory at {cwd}")
        return 1
    args, unknown_args = parse_args()
    check_gitignore()
    check_aiderignore()
    config = create_or_load_config()
    if args.upgrade:
        upgrade_aider()
        config["aider_update_info"] = {}  # Purge stale update info
        save_config(config)
        return 0
    if args.set_key:
        print("Setting openai key")
        config["openai_key"] = args.set_key
        save_config(config)
        config = create_or_load_config()
    if args.set_anthropic_key:
        print("Setting anthropic key")
        config["anthropic_key"] = args.set_anthropic_key
        save_config(config)
        config = create_or_load_config()
    anthropic_key = config.get("anthropic_key")
    openai_key = config.get("openai_key")
    model = get_model(args, anthropic_key, openai_key)
    install_aider_if_missing()
    is_anthropic_model = model in CLAUD3_MODELS
    if is_anthropic_model:
        if anthropic_key is None:
            print("Claude key not found, please set one with --set-anthropic-key")
            return 1
        os.environ["ANTHROPIC_API_KEY"] = anthropic_key
    else:
        openai_key = config.get("openai_key")
        if openai_key is None:
            print("OpenAI key not found, please set one with --set-key")
            return 1
        os.environ["OPENAI_API_KEY"] = openai_key

    last_aider_update_info: dict[str, Union[str, bool]] = config.get(
        "aider_update_info", {}
    )
    update_info: Optional[AiderUpdateResult] = None
    if last_aider_update_info:
        try:
            update_info = AiderUpdateResult.from_json(last_aider_update_info)
            if update_info.error:
                warnings.warn(f"Failed to parse update info: {update_info.error}")
                update_info = None
        except Exception as err:  # pylint: disable=broad-except
            warnings.warn(f"Failed to parse update info: {err}")
            update_info = None

    if update_info is not None and update_info.has_update:
        print(update_info.get_update_msg())

    # Note: Aider no longer uses ChatGPT 3.5 turbo by default. Therefore
    # it may soon no longer be necessary to specify the model.
    os.environ["AIDER_MODEL"] = model
    print(f"Starting aider with model {os.environ['AIDER_MODEL']}")
    # os.environ["OPENAI_API_KEY"] = openai_key
    cmd_list = ["aider", "--no-check-update"]
    if is_anthropic_model:
        cmd_list.append("--sonnet")
    if args.auto_commit:
        cmd_list.append("--auto-commit")
    else:
        cmd_list.append("--no-auto-commit")
    args.prompt = fix_paths(args.prompt)
    cmd_list += args.prompt + unknown_args
    print("\nLoading aider:\n  remember to use /help for a list of commands\n")
    # Perform update in the background.
    update_thread = Thread(target=background_update_task, args=(config,))
    update_thread.daemon = True
    update_thread.start()

    rtn = subprocess.call(cmd_list)
    if args.keep:
        return rtn
    atexit.register(cleanup)
    if rtn != 0:
        # debug by showing where the aider executable is
        aider_path = shutil.which("aider")
        if aider_path is not None:
            print("aider executable found at", aider_path)
        else:
            print("aider executable not found")
    return rtn


def main() -> int:
    try:
        return cli()
    except KeyboardInterrupt:
        return 1
    except SystemExit as err:
        rtn = err.code
        if rtn is None:
            return 0
        if isinstance(rtn, int):
            return rtn
        return 1


if __name__ == "__main__":
    sys.exit(main())
