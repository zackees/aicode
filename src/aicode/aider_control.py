import shutil
import subprocess
import sys
import warnings
from pathlib import Path

from iso_env import IsoEnv, IsoEnvArgs, Requirements

from aicode.aider_update_result import AiderUpdateResult
from aicode.config import Config
from aicode.paths import AIDER_INSTALL_PATH
from aicode.util import extract_version_string

REQUIREMENTS_TXT = """
aider-chat[playwright,browser]
dotenv
"""


# AIDER_CHAT = "git+https://github.com/Aider-AI/aider.git@main#egg=aider"
# # REQUIREMENTS = [AIDER_CHAT]
# PYPROJECT_TOML = """
# [build-system]
# requires = ["setuptools>=42", "wheel"]
# build-backend = "setuptools.build_meta"

# [project]
# name = "my_project"
# version = "0.1.0"
# requires-python = ">=3.11, <3.12"
# dependencies = [
#     "aider-chat @ git+https://github.com/Aider-AI/aider.git"
# ]
# """


def _get_highest_version_path(path: Path) -> Path:
    subpaths = list(path.iterdir())
    # paths will be labeled with 0, 1, 2, 3, etc.
    path_ints = [int(p.name) for p in subpaths if p.is_dir() if p.name.isdigit()]
    path_ints.sort()
    if path_ints:
        return path / str(path_ints[-1])
    return path


def _get_next_install_path(path: Path) -> Path:
    subpaths = list(path.iterdir())
    # paths will be labeled with 0, 1, 2, 3, etc.
    path_ints = [int(p.name) for p in subpaths if p.is_dir() if p.name.isdigit()]
    if path_ints:
        return path / str(max(path_ints) + 1)
    return path / "0"


def _get_path(path: Path | None) -> Path:
    if path:
        return path
    return _get_highest_version_path(AIDER_INSTALL_PATH)


def _save_install_breadcrumb(path: Path) -> None:
    """Saves a breadcrumb file to indicate that the installation was successful."""
    (path / "installed").touch()


def _has_install_breadcrumb(path: Path) -> bool:
    """Checks if the installation breadcrumb file exists."""
    return (path / "installed").exists()


def get_iso_env(path: Path) -> IsoEnv:
    """Creates and returns an IsoEnv instance"""
    args = IsoEnvArgs(
        venv_path=path / ".venv",
        build_info=Requirements(REQUIREMENTS_TXT, python_version="==3.11.*"),
    )
    return IsoEnv(args)


def aider_fetch_update_status(path: Path | None = None) -> AiderUpdateResult:
    """Fetches the update string if it exists, else returns None if up to date"""
    path = _get_path(path)
    cp = aider_run(
        ["aider", "--just-check-update"],
        path=path,
        capture_output=True,
        check=False,
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
    path = _get_path(path)
    return _has_install_breadcrumb(path)


def aider_run(
    cmd_list: list[str], path: Path | None = None, **process_args
) -> subprocess.CompletedProcess:
    """Runs the command using the isolated environment."""
    path = _get_path(path)
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
    path = _get_next_install_path(path)
    if aider_installed(path):
        return

    # print("Installing aider...")
    print(f"Installing aider to {path}...")
    path.mkdir(exist_ok=True, parents=True)

    # noqa: F841 - IsoEnv constructor creates the environment even if we don't use the returned object
    iso = get_iso_env(path)
    iso.run(["aider", "--version"], check=True)
    _save_install_breadcrumb(path)
    print("Aider installed successfully.")


def aider_install_path() -> str | None:
    which = "which" if not sys.platform == "win32" else "where"
    if not aider_installed():
        return None
    cp = aider_run([which, "aider"], check=True, capture_output=True)
    return cp.stdout.strip()


def aider_upgrade(path: Path | None = None) -> int:
    print("Upgrading aider...")
    try:
        # aider_purge(path)
        aider_install(path)
        return 0
    except Exception as e:
        warnings.warn(f"Error upgrading aider: {e}")
        return 1


def aider_purge(path: Path | None = None, config: Config | None = None) -> int:
    print("Purging aider...")
    path = path or AIDER_INSTALL_PATH
    try:
        shutil.rmtree(path, ignore_errors=True)
        print("Aider purged successfully.")
        if config is not None:
            print("Purging update info...")
            config.aider_update_info = {}  # Purge stale update info
            config.save()
        return 0
    except Exception as e:
        print(f"Error purging aider: {e}")
        return 1
