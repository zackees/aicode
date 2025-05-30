import argparse
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


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


class CustomHelpParser(argparse.ArgumentParser):
    def print_help(self):
        from aicode.aider_control import aider_installed

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
        sys.exit(0)  # make sure and return exit 0 on help message.


@dataclass
class Args:
    prompt: list[str] = field(default_factory=list)
    set_key: str | None = None
    set_anthropic_key: str | None = None
    set_gemini_key: str | None = None
    open_aider_path: bool = False
    purge: bool = False
    upgrade: bool = False
    keep: bool = False
    auto_commit: bool = False
    no_watch: bool = False
    lint: bool = False
    no_architect: bool = False
    claude: bool = False
    gemini: bool = False
    model: str | None = None
    chatgpt: bool = False
    gui: bool = False
    cli: bool = False
    message_file: Path | None = None
    unknown_args: list[str] = field(default_factory=list)

    @staticmethod
    def parse(args: list[str] | None = None) -> "Args":
        return _parse_args(args)


def _parse_args(args: list[str] | None) -> Args:
    from aicode.models import MODEL_CHOICES
    from aicode.paths import AIDER_INSTALL_PATH

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
    argparser.add_argument("--set-gemini-key", help="Set Gemini key")
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
        "-d",
        "--deep",
        action="store_true",
        help="Usses architect mode",
    )
    argparser.add_argument(
        "--message-file",
        type=Path,
        help="Path to a file containing messages to send to aider",
    )
    model_group = argparser.add_mutually_exclusive_group()
    model_group.add_argument(
        "--claude",
        action="store_true",
        help="Use Claude model",
    )
    model_group.add_argument(
        "--gemini",
        action="store_true",
        help="Use Google Gemini model",
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
    parsed, unknown_args = argparser.parse_known_args(args)

    prompt = fix_paths(parsed.prompt)

    no_architect = not parsed.deep

    # Construct and return the Args dataclass instance
    return Args(
        prompt=prompt,
        set_key=parsed.set_key,
        set_anthropic_key=parsed.set_anthropic_key,
        set_gemini_key=parsed.set_gemini_key,
        open_aider_path=parsed.open_aider_path,
        purge=parsed.purge,
        upgrade=parsed.upgrade,
        keep=parsed.keep,
        auto_commit=parsed.auto_commit,
        no_watch=parsed.no_watch,
        lint=parsed.lint,
        no_architect=no_architect,
        claude=parsed.claude,
        gemini=parsed.gemini,
        model=parsed.model,
        chatgpt=parsed.chatgpt,
        gui=parsed.gui,
        cli=parsed.cli,
        unknown_args=unknown_args,
    )
