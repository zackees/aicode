import time
from threading import Thread


def _background_update_task(config: dict) -> None:
    from aicode.aider_control import aider_fetch_update_status
    from aicode.openaicfg import save_config

    try:
        # Wait for aider to start so that we don't impact startup time.
        # This is really needed for windows because startup is so slow.
        time.sleep(5)
        update_info = aider_fetch_update_status()
        config["aider_update_info"] = update_info.to_json_data()
        save_config(config)
    except KeyboardInterrupt:
        pass
    except SystemExit:
        pass


def background_update_task(config: dict) -> Thread:
    update_thread = Thread(target=_background_update_task, args=(config,))
    update_thread.daemon = True
    update_thread.start()
    return update_thread
