def run_process(cmd_list: list[str]) -> int:
    """Todo this will be replaced with something more interactive."""
    from aicode.aider_control import aider_run

    rtn = aider_run(cmd_list).returncode
    return rtn
