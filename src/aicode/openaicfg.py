import json
import os
from pathlib import Path

from appdirs import user_config_dir  # type: ignore
from semi_secret import SecretStorage  # type: ignore

# Create SHA1 hash of the storage key
STORAGE_KEY = "aicode_openai_config"
SALT = "aicode_salt"  # We should use a consistent salt for the storage

STORAGE_PATH = Path(user_config_dir("advanced-aicode", roaming=True))

# Initialize storage once
_storage = SecretStorage(STORAGE_KEY, SALT, storage_path=STORAGE_PATH)


def _get_config_path_legacy() -> str:
    env_path = user_config_dir("zcmds", "zcmds", roaming=True)
    config_file = os.path.join(env_path, "openai.json")
    return config_file


def save_config(config: dict) -> None:
    """Save the config using semi-secret storage."""
    _storage.set("config", json.dumps(config))


def load_from_storage() -> dict:
    """Load the config from semi-secret storage."""
    config_str = _storage.get("config")
    if config_str:
        return json.loads(config_str)
    return {}


def _create_or_load_config_legacy() -> dict:
    config_file = _get_config_path_legacy()
    try:
        with open(config_file, encoding="utf-8", mode="r") as f:
            config = json.loads(f.read())
        return config
    except OSError:
        save_config({})
        return {}


def create_or_load_config() -> dict:
    # First, try to load from semi-secret storage
    config = load_from_storage()
    if config:
        return config

    # If not in storage, try to load from file (for backwards compatibility)
    config = _create_or_load_config_legacy()

    # If loaded from file, save to storage for future use
    if config:
        save_config(config)

    return config
