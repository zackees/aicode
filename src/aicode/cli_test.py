"""aicode - front end for aider"""

import sys

from aicode.cli import cli


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
    sys.argv.append("--model")
    sys.argv.append("o3")  # Default model for testing
    sys.exit(main())
