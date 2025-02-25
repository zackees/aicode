import os
import re
import subprocess
import sys
import warnings
from pathlib import Path


def extract_version_string(version_string: str) -> str:
    """
    Extracts version strings like "v0.22.0", "0.40.5-dev" out of messages.
    """
    match = re.search(r"v?\d+\.\d+\.\d+(-\w+)?", version_string)
    if match:
        return match.group()
    raise ValueError(f"Failed to extract version string from {version_string}")


def open_folder(path: Path) -> None:
    if sys.platform == "win32":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def _find_path_to_git_directory(cwd: Path) -> Path:
    path = cwd.absolute()  # Make sure we have absolute path
    while True:
        if (path / ".git").exists():
            return path
        parent = path.parent
        if parent == path:  # We've hit the root
            break
        path = parent
    raise FileNotFoundError("No git directory found")


def check_gitdirectory() -> bool:
    try:
        cwd = Path.cwd()
        path = _find_path_to_git_directory(cwd=cwd)
        print("Found git directory at", path)
        os.chdir(str(path))
        return True
    except FileNotFoundError:
        return False


def cleanup_chat_history(cwd: Path) -> None:
    files = [
        ".aider.chat.history.md",
        ".aider.input.history",
    ]
    for file in files:
        file_path = cwd / file
        if file_path.exists():
            try:
                file_path.unlink()
            except OSError:
                warnings.warn(f"Failed to remove {file_path}")
