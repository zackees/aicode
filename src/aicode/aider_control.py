import subprocess
from pathlib import Path

from isolated_environment import isolated_environment, isolated_environment_run

from aicode.aider_update_result import AiderUpdateResult
from aicode.util import extract_version_string

HERE = Path(__file__).parent

REQUIREMENTS = [
    "aider-chat[playwright]",
]


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


def aider_run(cmd_list: list[str], **process_args) -> subprocess.CompletedProcess:
    """Runs the command using the isolated environment."""
    cp = isolated_environment_run(
        env_path=HERE / "aider-install",
        requirements=REQUIREMENTS,
        cmd_list=cmd_list,
        **process_args,
    )
    return cp


def aider_install() -> None:
    """Uses isolated_environment to install aider."""
    # Print installing message
    print("Installing aider...")
    # Install aider using isolated_environment
    isolated_environment(
        env_path=HERE / "aider-install", requirements=REQUIREMENTS, full_isolation=True
    )


def aider_installed() -> bool:
    cp = isolated_environment_run(
        env_path=HERE / "aider-install",
        requirements=REQUIREMENTS,
        cmd_list=["aider", "--version"],
        capture_output=True,
    )
    return cp.returncode == 0


def aider_install_path() -> str | None:
    if not aider_installed():
        return None
    cp = isolated_environment_run(
        env_path=HERE / "aider-install",
        requirements=REQUIREMENTS,
        cmd_list=["which", "aider"],
        capture_output=True,
    )
    return cp.stdout.strip()


def aider_upgrade() -> int:
    print("Upgrading aider...")

    if not aider_installed():
        aider_install()
        return 0

    cp = isolated_environment_run(
        env_path=HERE / "aider-install",
        requirements=REQUIREMENTS,
        cmd_list=["pip", "install", "--upgrade", "aider-chat[playwright]"],
        check=False,
    )
    return cp.returncode
