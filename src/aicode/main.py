"""aicode - front end for aider"""

import atexit
import os
import sys
import warnings

from aicode.aider_control import (
    aider_install,
    aider_install_path,
    aider_installed,
)
from aicode.args import Args
from aicode.background import background_update_task
from aicode.build_cmd_list import build_cmd_list_or_die
from aicode.run_process import run_process

# This will be at the root of the project, side to the .git directory
AIDER_HISTORY = ".aider.chat.history.md"


def aider_install_if_missing() -> None:
    # Set the custom bin path where you want aider to be installed
    # Check if aider is already installed
    if aider_installed():
        return
    aider_install()


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


def cli() -> int:
    args: Args = Args.parse()
    cmd_list: list[str]
    config: dict
    cmd_list, config = build_cmd_list_or_die(args)
    print("\nLoading aider:\n  remember to use /help for a list of commands\n")
    # Perform update in the background.
    _ = background_update_task(config=config)
    print("\n" + "=" * 80)
    print("RUNNING COMMAND:")
    print(" ".join(cmd_list))
    print("=" * 80 + "\n")

    # rtn = subprocess.call(cmd_list)
    rtn = run_process(cmd_list)
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
