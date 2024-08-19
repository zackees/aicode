import shutil
import subprocess
import sys
import warnings


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


def upgrade_aider() -> int:
    print("Upgrading aider...")
    # rtn = os.system("pipx upgrade aider-chat")
    PYTHON_EXE = sys.executable
    rtn = subprocess.run(f"{PYTHON_EXE} -m pip install --upgrade aider-chat").returncode
    if rtn == 0:
        print("Upgrade successful.")
        return 0
    warnings.warn("Upgrade failed, pipx may be out of date.")
    yes = input("Would you like to try upgrading pipx? [y/N] ")
    if yes.lower() != "y":
        return 0
    print("Upgrading pipx...")
    PYTHON_EXE = sys.executable
    # rtn = os.system(f'"{PYTHON_EXE}" -m pip install --upgrade pipx')
    rtn = subprocess.run(f"{PYTHON_EXE} -m pip install --upgrade pipx").returncode
    if rtn != 0:
        warnings.warn("Failed to upgrade pipx.")
        return rtn
    rtn = upgrade_aider()
    if rtn == 0:
        print("Reinstall successful.")
        return 0
    warnings.warn("Failed to upgrade aider.")
    return rtn
