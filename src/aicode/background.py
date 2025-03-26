import subprocess
import time
import warnings
from threading import Thread

from aicode.config import Config


def _background_update_task(config: Config) -> None:
    from aicode.aider_control import aider_fetch_update_status
    from aicode.openaicfg import save_config

    try:
        # Wait for aider to start so that we don't impact startup time.
        # This is really needed for windows because startup is so slow.
        time.sleep(5)
        update_info = aider_fetch_update_status()
        config.aider_update_info = update_info.to_json_data()
        save_config(config.to_dict())
    except KeyboardInterrupt:
        pass
    except SystemExit:
        pass
    except subprocess.CalledProcessError as cpe:
        stdout: bytes | str = cpe.stdout
        stderr: bytes | str = cpe.stderr
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8")
        warnings.warn(
            f"Error checking for updates: {cpe}, rtn={cpe.returncode}, stdout={stdout}, stderr={stderr}"
        )
        pass
    except Exception as e:
        warnings.warn(f"Error checking for updates: {e}")
        pass


def background_update_task(config: Config) -> Thread:
    update_thread = Thread(target=_background_update_task, args=(config,))
    update_thread.daemon = True
    update_thread.start()
    return update_thread


def _test() -> None:
    config = Config()
    thread = background_update_task(config)
    thread.join()
    time.sleep(10)


if __name__ == "__main__":
    _test()
