import subprocess
import sys
from pathlib import Path

from aicode.aider_update_result import AiderUpdateResult
from aicode.util import extract_version_string

HERE = Path(__file__).parent
AIDER_INSTALL_PATH = HERE / "aider-install"

REQUIREMENTS = ["aider-chat[playwright]", "uv"]


def aider_fetch_update_status() -> AiderUpdateResult:
    """Fetches the update string if it exists, else returns None if up to date"""
    cp = aider_run(
        ["aider", "--just-check-update"],
        capture_output=True,
        check=False,
        universal_newlines=True,
    )
    lines = cp.stdout.strip().split("\n")
    update_available = None
    current_version = None
    latest_version = None
    for line in lines:
        if "Update available" in line:
            update_available = True
        if "Current version" in line:
            current_version = extract_version_string(line)
        if "Latest version" in line:
            latest_version = extract_version_string(line)
    if update_available is None:
        # Old way means update available when cp.returncode == 1
        update_available = cp.returncode == 1
    out = AiderUpdateResult(
        has_update=update_available,
        latest_version=latest_version if latest_version else "Unknown",
        current_version=current_version if current_version else "Unknown",
    )
    return out


def aider_installed() -> bool:
    return (AIDER_INSTALL_PATH / "installed").exists()


def aider_run(cmd_list: list[str], **process_args) -> subprocess.CompletedProcess:
    """Runs the command using the isolated environment."""
    if not aider_installed():
        aider_install()
    # $ uv run example.py
    cmd_list = get_activated_environment_cmd_list()
    cmd_list.extend(["aider", "--just-check-update"])
    cp = subprocess.run(cmd_list, cwd=str(AIDER_INSTALL_PATH), shell=True, **process_args)
    return cp


def get_activated_environment_cmd_list() -> list[str]:
    cmd_list = []
    if sys.platform == "win32":
        cmd_list.append(".venv\\Scripts\\activate.bat")
    elif sys.platform == "darwin":
        cmd_list.append(".venv/bin/activate")
    else:
        # linux
        cmd_list.append("source")
        cmd_list.append(".venv/bin/activate")
    cmd_list.append("&&")
    return cmd_list


def aider_install() -> None:
    """Uses isolated_environment to install aider."""
    if aider_installed():
        return
    # Print installing message
    print("Installing aider...")
    # Install aider using isolated_environment
    AIDER_INSTALL_PATH.mkdir(exist_ok=True)
    subprocess.run(["uv", "venv"], cwd=str(AIDER_INSTALL_PATH), check=True)
    requirements = AIDER_INSTALL_PATH / "requirements.txt"
    requirements.write_text("\n".join(REQUIREMENTS))
    cmd_list = get_activated_environment_cmd_list()
    cmd_list.extend(["uv", "pip", "install", "-r", "requirements.txt"])
    subprocess.run(cmd_list, cwd=str(AIDER_INSTALL_PATH), check=True)
    if sys.platform not in ["win32", "darwin"]:
        # linux
        subprocess.run(["chmod", "+x", str(AIDER_INSTALL_PATH / "bin" / "activate")], cwd=str(AIDER_INSTALL_PATH), check=True, shell=True)
    # add a file to indicate that the installation was successful
    (AIDER_INSTALL_PATH / "installed").touch()


def aider_install_path() -> str | None:
    which = "which" if not sys.platform == "win32" else "where"
    if not aider_installed():
        return None
    cp = aider_run([which, "aider"], check=True, capture_output=True)
    return cp.stdout.strip()


def aider_upgrade() -> int:
    print("Upgrading aider...")

    if not aider_installed():
        aider_install()
        return 0
    cp = aider_run(["aider", "--upgrade"], check=True)
    return cp.returncode
