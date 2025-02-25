"""aicode - front end for aider"""

import argparse
import atexit
import os
import subprocess
import sys
import time
import warnings
from dataclasses import dataclass, field
from os.path import exists
from pathlib import Path
from threading import Thread
from typing import Optional, Union

from aicode.aider_control import (
    aider_fetch_update_status,
    aider_install,
    aider_install_path,
    aider_installed,
    aider_purge,
    aider_run,
    aider_upgrade,
)
from aicode.aider_update_result import AiderUpdateResult, Version
from aicode.openaicfg import create_or_load_config, save_config
from aicode.paths import AIDER_INSTALL_PATH

CHAT_GPT = "openai/gpt-4o"

# This will be at the root of the project, side to the .git directory
AIDER_HISTORY = ".aider.chat.history.md"


@dataclass
class Model:
    name: str
    description: str
    model_str: str


MODELS = {
    "chatgpt": Model("gpt-4o", "The GPT-4o model.", CHAT_GPT),
    "claude": Model(
        "claude", "The Claude model.", "anthropic/claude-3-7-sonnet-20250219"
    ),
    "deepseek": Model(
        "deepseek",
        "The deepseek model.",
        "deepseek",
    ),
}

CLAUD3_MODELS = {"claude"}

MODEL_CHOICES = list(MODELS.keys())
_ENABLE_HISTORY_ASK = False


def aider_install_if_missing() -> None:
    # Set the custom bin path where you want aider to be installed
    # Check if aider is already installed
    if aider_installed():
        return
    aider_install()


class CustomHelpParser(argparse.ArgumentParser):
    def print_help(self):
        # Call the default help message
        super().print_help()
        is_installed = aider_installed()
        if not is_installed:
            print("aider is not installed, no more help available.")
            sys.exit(0)
        print("\n\n############ aider --help ############")
        completed_proc = subprocess.run(
            ["aider", "--help"], check=False, capture_output=True, text=True
        )
        stdout = completed_proc.stdout
        print(stdout)
        # flush print buffer
        sys.stdout.flush()
        sys.exit(0)
        # make sure and return exit 0 on help message.


@dataclass
class Args:
    prompt: list[str] = field(default_factory=list)
    set_key: Optional[str] = None
    set_anthropic_key: Optional[str] = None
    open_aider_path: bool = False
    purge: bool = False
    upgrade: bool = False
    keep: bool = False
    auto_commit: bool = False
    no_watch: bool = False
    lint: bool = False
    no_architect: bool = False
    claude: bool = False
    model: Optional[str] = None
    chatgpt: bool = False
    gui: bool = False
    cli: bool = False
    unknown_args: list[str] = field(default_factory=list)


def parse_args() -> Args:
    CustomHelpParser = argparse.ArgumentParser
    argparser = CustomHelpParser(
        usage=(
            "Ask OpenAI for help with code, uses aider-chat on the backend. "
            "Any args not listed here are assumed to be for aider and will be passed on to it.\n"
            f"The real aider install path will be located at {AIDER_INSTALL_PATH}"
        )
    )
    argparser.add_argument("prompt", nargs="*", help="Args to pass onto aider")
    argparser.add_argument("--set-key", help="Set OpenAI key")
    argparser.add_argument("--set-anthropic-key", help="Set Claude key")
    argparser.add_argument(
        "--open-aider-path",
        action="store_true",
        help="Opens the real path to aider if it's installed.",
    )
    argparser.add_argument(
        "--purge", action="store_true", help="Purge aider installation"
    )
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
        help="Automatically commit changes",
    )
    argparser.add_argument(
        "--no-watch",
        action="store_true",
        help="Disable aider watch mode, which is enabled by default",
    )
    argparser.add_argument(
        "--lint",
        action="store_true",
        help="Enable auto-linting",
    )
    argparser.add_argument(
        "--no-architect",
        action="store_true",
        help="Disable architect mode",
    )
    model_group = argparser.add_mutually_exclusive_group()
    model_group.add_argument(
        "--claude",
        action="store_true",
        help="Use Claude model",
    )
    model_group.add_argument("--model", choices=MODEL_CHOICES, help="Model to use")
    model_group.add_argument(
        "--chatgpt",
        action="store_true",
        help="Use ChatGPT model",
    )
    gui_group = argparser.add_mutually_exclusive_group()
    gui_group.add_argument(
        "--gui",
        action="store_true",
        help="Use GUI mode",
    )
    gui_group.add_argument(
        "--cli",
        action="store_true",
        help="Use CLI mode (default)",
    )

    # Parse known arguments, leaving unknown args for aider
    parsed, unknown_args = argparser.parse_known_args()

    # Construct and return the Args dataclass instance
    return Args(
        prompt=parsed.prompt,
        set_key=parsed.set_key,
        set_anthropic_key=parsed.set_anthropic_key,
        open_aider_path=parsed.open_aider_path,
        purge=parsed.purge,
        upgrade=parsed.upgrade,
        keep=parsed.keep,
        auto_commit=parsed.auto_commit,
        no_watch=parsed.no_watch,
        lint=parsed.lint,
        no_architect=parsed.no_architect,
        claude=parsed.claude,
        model=parsed.model,
        chatgpt=parsed.chatgpt,
        gui=parsed.gui,
        cli=parsed.cli,
        unknown_args=unknown_args,
    )


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


def get_interface_mode(args: Args) -> bool:
    """Returns True for GUI mode, False for CLI mode"""
    if args.gui:
        return True
    if args.cli:
        return False

    while True:
        try:
            answer = input("Select interface:\n  [0] CLI\n  [1] GUI\nChoice [0]: ")
            if answer.strip() == "":
                return False
            choice = int(answer)
            if choice == 0:
                return False
            if choice == 1:
                return True
            print("Please enter 0 or 1")
        except ValueError:
            print("Please enter a valid number (0 or 1)")


def get_model(
    args: Args, anthropic_key: Optional[str], openai_key: Optional[str]
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
        update_info = aider_fetch_update_status()
        config["aider_update_info"] = update_info.to_json_data()
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


def get_lint_command() -> Optional[str]:
    if exists("./lint"):
        return "./lint"
    return None


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
    path = cwd.absolute()  # Make sure we have absolute path
    while True:
        if (path / ".git").exists():
            return path
        parent = path.parent
        if parent == path:  # We've hit the root
            break
        path = parent
    raise FileNotFoundError("No git directory found")


def check_gitdirectory() -> bool:
    try:
        cwd = Path.cwd()
        path = find_path_to_git_directory(cwd=cwd)
        print("Found git directory at", path)
        os.chdir(str(path))
        return True
    except FileNotFoundError:
        return False


def _open_folder(path: Path) -> None:
    if sys.platform == "win32":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def cli() -> int:
    # does .git directory exist?
    # args, unknown_args = parse_args()
    args: Args = parse_args()
    unknown_args = args.unknown_args
    config = create_or_load_config()
    if args.open_aider_path:
        print("Opening the real path to aider.")
        path = AIDER_INSTALL_PATH
        if path is not None:
            print(path)
            _open_folder(path)
            return 0
        else:
            warnings.warn("aider executable not found")
            return 1
    if args.purge:
        print("Purging aider installation")
        aider_purge()
        config["aider_update_info"] = {}
        save_config(config)
        return 0

    if args.upgrade:
        aider_upgrade()
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
    has_git = check_gitdirectory()

    check_gitignore()
    check_aiderignore()
    anthropic_key = config.get("anthropic_key")
    openai_key = config.get("openai_key")
    model = get_model(args, anthropic_key, openai_key)
    aider_install_if_missing()
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

    # C:\\Users\\niteris\\dev\\aicode\\.venv\\Scripts\\uv.EXE run --project C:\\Users\\niteris\\AppData\\Local\\aider-install\\aider\\.venv aider.chat --no-check-update --gui --sonnet --no-auto-commit --architect --no-auto-lint --watch

    use_gui = get_interface_mode(args)

    if os.path.exists(AIDER_HISTORY) and _ENABLE_HISTORY_ASK:
        answer = (
            input("Chat history found. Would you like to restore it? [y/N]: ")
            .strip()
            .lower()
        )
        if answer in ("y", "yes"):
            cmd_list = ["aider", "--no-check-update", "--restore-chat-history"]
        else:
            cmd_list = ["aider", "--no-check-update"]
    else:
        cmd_list = ["aider", "--no-check-update"]

    if use_gui:
        cmd_list.append("--gui")
    if is_anthropic_model:
        cmd_list.append("--sonnet")
    if args.auto_commit:
        cmd_list.append("--auto-commit")
    else:
        cmd_list.append("--no-auto-commit")
    # New feature to enable architect mode which seems to vastly
    # improve the code editing capatility of the various ai coding models.
    if not args.no_architect:
        cmd_list.append("--architect")
    if args.lint:
        lint_cmd = get_lint_command()
        if lint_cmd:
            cmd_list.extend(["--lint-cmd", lint_cmd])
        else:
            cmd_list.append("--auto-lint")
    else:
        cmd_list.append("--no-auto-lint")
    if not has_git:
        cmd_list.append("--no-git")
    if not args.no_watch:
        update_info = aider_fetch_update_status()
        current_version: Version | None = update_info.get_current_version()
        if update_info is not None:
            min_version = Version("0.70.0")
            if current_version >= min_version:
                cmd_list.append("--watch")
    args.prompt = fix_paths(args.prompt)
    cmd_list += args.prompt + unknown_args
    print("\nLoading aider:\n  remember to use /help for a list of commands\n")
    # Perform update in the background.
    update_thread = Thread(target=background_update_task, args=(config,))
    update_thread.daemon = True
    update_thread.start()

    print("\n" + "=" * 80)
    print("RUNNING COMMAND:")
    print(" ".join(cmd_list))
    print("=" * 80 + "\n")

    # rtn = subprocess.call(cmd_list)
    rtn = aider_run(cmd_list).returncode
    if args.keep:
        return rtn
    atexit.register(cleanup)
    if rtn != 0:
        # debug by showing where the aider executable is
        aider_path = aider_install_path()
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
