import os
import subprocess
import sys


def main() -> int:
    """Main function."""
    prev_cwd = os.getcwd()
    try:
        cwd = sys.argv[1]
        os.chdir(cwd)
        sys.argv.pop(1)
        args = subprocess.list2cmdline(sys.argv[1:])
        cp = subprocess.run(args, shell=True)
        return cp.returncode
    except KeyboardInterrupt:
        return 1
    finally:
        os.chdir(prev_cwd)


if __name__ == "__main__":
    sys.exit(main())
