import re


def extract_version_string(version_string: str) -> str:
    """
    Extracts version strings like "v0.22.0", "0.40.5-dev" out of messages.
    """
    match = re.search(r"v?\d+\.\d+\.\d+(-\w+)?", version_string)
    if match:
        return match.group()
    raise ValueError(f"Failed to extract version string from {version_string}")
