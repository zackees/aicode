import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))

CUSTOM_PATH = os.path.join(HERE, "aider-install")


def init_env() -> None:
    os.environ["PIPX_HOME"] = CUSTOM_PATH
    os.environ["PIPX_BIN_DIR"] = os.path.join(CUSTOM_PATH, "bin")
    os.environ["PATH"] = os.environ["PATH"] + os.pathsep + os.environ["PIPX_BIN_DIR"]
    print(f"Real aider is at {shutil.which('aider')}")


init_env()
