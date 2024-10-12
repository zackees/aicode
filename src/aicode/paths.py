from pathlib import Path

from appdirs import user_config_dir  # type: ignore


def _get_aider_install_path(path: Path | None = None) -> Path:
    if path is None:
        default_path: str = user_config_dir("aider", "aider-install", roaming=False)
        path = Path(default_path)
    return path


AIDER_INSTALL_PATH = _get_aider_install_path()
