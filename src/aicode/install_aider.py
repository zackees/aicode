import shutil
import subprocess
import sys


def install_aider() -> None:
    # Print installing message
    print("Installing aider...")

    # Get the current Python executable
    PYTHON_EXE = sys.executable

    # Install aider using pipx in the custom bin path
    cmd = f'"{PYTHON_EXE}" -m pipx install aider-chat'
    completed_proc = subprocess.run(cmd, check=False, shell=True)
    # Ensure installation was successful
    if completed_proc.returncode != 0:
        assert False, "Failed to install aider"
    assert shutil.which("aider") is not None, "aider not found after install"
