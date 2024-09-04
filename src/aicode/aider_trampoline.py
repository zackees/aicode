import os
import subprocess
import sys


def main() -> int:
    """Main function."""
    cwd = sys.argv[1]
    os.chdir(cwd)
    sys.argv.pop(1)
    # print(f"Working directory: {cwd}")
    os.chdir(cwd)
    args = subprocess.list2cmdline(sys.argv[1:])
    # print(f"Running: {args}")
    cp = subprocess.run(args, shell=True)
    return cp.returncode


if __name__ == "__main__":
    sys.exit(main())
