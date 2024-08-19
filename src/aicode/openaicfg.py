import json
import os

import keyring
from appdirs import user_config_dir  # type: ignore

KEYRING_SERVICE_NAME = "aicode_openai"
KEYRING_USERNAME = "config"


def _get_config_path_legacy() -> str:
    env_path = user_config_dir("zcmds", "zcmds", roaming=True)
    config_file = os.path.join(env_path, "openai.json")
    return config_file


def save_config(config: dict) -> None:
    """Save the config to the keyring."""
    keyring.set_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME, json.dumps(config))


def load_from_keyring() -> dict:
    """Load the config from the keyring."""
    config_str = keyring.get_password(KEYRING_SERVICE_NAME, KEYRING_USERNAME)
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
    # First, try to load from keyring
    config = load_from_keyring()
    if config:
        return config

    # If not in keyring, try to load from file (for backwards compatibility)
    config = _create_or_load_config_legacy()

    # If loaded from file, save to keyring for future use
    if config:
        save_config(config)

    return config
