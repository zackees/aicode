import re
import subprocess

from aicode.aider_update_result import AiderUpdateResult


def aider_fetch_update_status() -> AiderUpdateResult:
    """Fetches the update string if it exists, else returns None if up to date"""
    cp = subprocess.run(
        ["aider", "--just-check-update"],
        check=False,
        capture_output=True,
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


def extract_version_string(version_string: str) -> str:
    """
    Extracts version strings like "v0.22.0", "0.40.5-dev" out of messages.
    """
    match = re.search(r"v?\d+\.\d+\.\d+(-\w+)?", version_string)
    if match:
        return match.group()
    raise ValueError(f"Failed to extract version string from {version_string}")
