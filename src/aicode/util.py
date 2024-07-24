import re
import subprocess


def aider_fetch_update_string_if_out_of_date() -> str | None:
    """Fetches the update string if it exists, else returns None if up to date"""
    cp = subprocess.run(
        ["aider", "--just-check-update"],
        check=False,
        capture_output=True,
        universal_newlines=True,
    )
    if cp.returncode == 0:  # Zero code means no update.
        return None
    raw_str = cp.stdout.strip()
    return extract_version_string(raw_str)


def extract_version_string(version_string: str) -> str:
    """
    Extracts version strings like "v0.22.0", "0.40.5-dev" out of messages.
    """
    match = re.search(r"v?\d+\.\d+\.\d+(-\w+)?", version_string)
    if match:
        return match.group()
    raise ValueError(f"Failed to extract version string from {version_string}")
