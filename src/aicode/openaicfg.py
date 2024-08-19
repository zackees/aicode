import json
import os
import shutil
import warnings

from appdirs import user_config_dir  # type: ignore


def get_config_path_legacy() -> str:
    env_path = user_config_dir("zcmds", "zcmds", roaming=True)
    config_file = os.path.join(env_path, "openai.json")
    return config_file


def get_config_path_new() -> str:
    env_path = user_config_dir("aicode", roaming=True)
    config_file = os.path.join(env_path, "openai.json")
    return config_file


def get_config_path() -> str:
    """Gently migrate users to the new config path."""
    config_path = get_config_path_new()
    if os.path.exists(config_path):
        return config_path
    config_path = get_config_path_legacy()
    if os.path.exists(config_path):
        try:
            shutil.copy(config_path, get_config_path_new())
        except OSError:
            warnings.warn(
                f"Failed to copy config file from {config_path} to {get_config_path_new()}"
            )
    return get_config_path_new()


def save_config(config: dict) -> None:
    config_file = get_config_path()
    # make all subdirs of config_file
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    with open(config_file, encoding="utf-8", mode="w") as f:
        json.dump(config, f)


def create_or_load_config() -> dict:
    config_file = get_config_path()
    try:
        with open(config_file, encoding="utf-8", mode="r") as f:
            config = json.loads(f.read())
        return config
    except OSError:
        save_config({})
        return {}
