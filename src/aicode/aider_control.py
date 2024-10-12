import os
import shutil
import subprocess
import sys
import warnings
from pathlib import Path

from aicode.aider_update_result import AiderUpdateResult
from aicode.paths import AIDER_INSTALL_PATH
from aicode.util import extract_version_string

HERE = Path(__file__).parent

AIDER_CHAT = "aider-chat[playwright]"
REQUIREMENTS = [AIDER_CHAT, "uv"]


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


def aider_installed(path: Path | None = None) -> bool:
    path = path or AIDER_INSTALL_PATH
    dst = path / "aider_trampoline.py"
    if not dst.exists():
        path.mkdir(parents=True, exist_ok=True)
        shutil.copy(HERE / "aider_trampoline.py", path / "aider_trampoline.py")
    return (path / "installed").exists()


def aider_run(
    cmd_list: list[str], path: Path | None = None, **process_args
) -> subprocess.CompletedProcess:
    path = path or AIDER_INSTALL_PATH
    """Runs the command using the isolated environment."""
    if not aider_installed(path):
        aider_install(path)
    full_cmd = ["uv", "run", "aider_trampoline.py", os.getcwd()] + cmd_list
    full_cmd_str = subprocess.list2cmdline(full_cmd)
    env = dict(os.environ)
    env["VIRTUAL_ENV"] = str(path / ".venv")
    cp = subprocess.run(full_cmd_str, cwd=path, env=env, shell=True, **process_args)
    return cp


def aider_install(path: Path | None = None) -> None:
    """Uses isolated_environment to install aider."""
    path = path or AIDER_INSTALL_PATH
    if aider_installed(path):
        return
    # Print installing message
    print("Installing aider...")
    # Install aider using isolated_environment
    path.mkdir(exist_ok=True)
    subprocess.run(["uv", "venv"], cwd=str(path), check=True)
    requirements = path / "requirements.txt"
    requirements.write_text("\n".join(REQUIREMENTS))
    env: dict = dict(os.environ)
    env["VIRTUAL_ENV"] = str(path / ".venv")
    subprocess.run(
        "uv pip install -r requirements.txt",
        cwd=str(path),
        env=env,
        shell=True,
        check=True,
    )

    # delete this file.
    # aider-install\Lib\site-packages\distutils-precedence.pth
    problematic_file = path / "Lib" / "site-packages" / "distutils-precedence.pth"
    if problematic_file.exists():
        try:
            problematic_file.unlink()
        except Exception as e:
            warnings.warn(f"Failed to delete {problematic_file}: {e}")

    # copy aider_control.py to the installation path
    # add a file to indicate that the installation was successful
    (path / "installed").touch()


def aider_install_path() -> str | None:
    which = "which" if not sys.platform == "win32" else "where"
    if not aider_installed():
        return None
    cp = aider_run([which, "aider"], check=True, capture_output=True)
    return cp.stdout.strip()


def aider_upgrade(path: Path | None = None) -> int:
    print("Upgrading aider...")
    path = path or AIDER_INSTALL_PATH
    if not aider_installed():
        aider_install()
        return 0
    upgrade_cmd = ["uv", "pip", "install", "--upgrade", AIDER_CHAT]

    try:
        cp = aider_run(upgrade_cmd, check=True, path=path)
        if cp.returncode != 0:
            print(f"Error upgrading aider: {cp.returncode}")
            return cp.returncode
        print("Aider upgraded successfully.")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Error upgrading aider: {e}")
        return e.returncode


def aider_purge(path: Path | None = None) -> int:
    print("Purging aider...")
    path = path or AIDER_INSTALL_PATH
    if not aider_installed():
        print("Aider is not installed.")
        return 0
    try:
        shutil.rmtree(path)
        print("Aider purged successfully.")
        return 0
    except Exception as e:
        print(f"Error purging aider: {e}")
        return 1
