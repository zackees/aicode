import shutil
import subprocess
import sys
from pathlib import Path

from iso_env import IsoEnv, IsoEnvArgs, Requirements

from aicode.aider_update_result import AiderUpdateResult
from aicode.paths import AIDER_INSTALL_PATH
from aicode.util import extract_version_string

AIDER_CHAT = "aider-chat[playwright]"
REQUIREMENTS = [AIDER_CHAT]


def get_iso_env(path: Path) -> IsoEnv:
    """Creates and returns an IsoEnv instance"""
    args = IsoEnvArgs(
        venv_path=path / ".venv",
        build_info=Requirements(AIDER_CHAT, python_version="==3.11.*"),
    )
    return IsoEnv(args)


def aider_fetch_update_status() -> AiderUpdateResult:
    """Fetches the update string if it exists, else returns None if up to date"""
    cp = aider_run(
        ["aider", "--just-check-update"],
        capture_output=True,
        check=True,
        text=False,
        universal_newlines=False,
        shell=False,
    )
    assert cp.stdout is not None
    stdout_bytes: bytes = cp.stdout
    stdout: str = stdout_bytes.decode("utf-8")
    lines = stdout.strip().split("\n")
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
    return (path / "installed").exists()


def aider_run(
    cmd_list: list[str], path: Path | None = None, **process_args
) -> subprocess.CompletedProcess:
    """Runs the command using the isolated environment."""
    path = path or AIDER_INSTALL_PATH
    if not aider_installed(path):
        aider_install(path)

    iso = get_iso_env(path)
    return iso.run(cmd_list, **process_args)

    # cwd = os.getcwd()
    # with iso.temp_path_context(cwd):
    #     return iso.run(cmd_list, **process_args)


def aider_install(path: Path | None = None) -> None:
    """Uses iso-env to install aider."""
    path = path or AIDER_INSTALL_PATH
    if aider_installed(path):
        return

    print("Installing aider...")
    path.mkdir(exist_ok=True, parents=True)

    # noqa: F841 - IsoEnv constructor creates the environment even if we don't use the returned object
    iso = get_iso_env(path)
    iso.run(["aider", "--version"], check=True)
    print("Aider installed successfully.")


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

    iso = get_iso_env(path)
    try:
        iso.run(["pip", "install", "--upgrade", AIDER_CHAT], check=True)
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
