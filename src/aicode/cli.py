"""aicode - front end for aider"""

import atexit
import subprocess
from pathlib import Path

from aicode.aider_control import (
    aider_install_path,
)
from aicode.args import Args
from aicode.background import background_update_task
from aicode.build_cmd_list import build_cmd_list_or_die
from aicode.config import Config
from aicode.run_process import run_process


def _to_args(args: Args | list[str] | None = None) -> Args:
    if isinstance(args, Args):
        return args
    return Args.parse(args=args)


def _print_cmd_list(cmd_list: list[str]) -> None:
    print("\n" + "=" * 80)
    print("RUNNING COMMAND:")
    cmd_str = subprocess.list2cmdline(cmd_list)
    print(cmd_str)
    print("=" * 80 + "\n")


def _register_cleanup_if_necessary(args: Args) -> None:
    from aicode.util import cleanup_chat_history

    if not args.keep:
        cwd_abs = Path.cwd().absolute()
        atexit.register(lambda: cleanup_chat_history(cwd_abs))


def cli(args: Args | list[str] | None = None) -> int:
    args = _to_args(args)
    _register_cleanup_if_necessary(args)
    cmd_list: list[str]
    config: Config
    cmd_list, config = build_cmd_list_or_die(args)
    print("\nLoading aider:\n  remember to use /help for a list of commands\n")
    # Perform update in the background.
    _ = background_update_task(config=config)
    _print_cmd_list(cmd_list)
    # rtn = subprocess.call(cmd_list)
    rtn = run_process(cmd_list)
    if rtn != 0:
        # debug by showing where the aider executable is
        aider_path = aider_install_path()
        if aider_path is not None:
            print("aider executable found at", aider_path)
        else:
            print("aider executable not found")
    return rtn
