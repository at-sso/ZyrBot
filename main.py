from src import ui
from src.function_wrapper import f_wrapper
from src.env import *
from src.env.ctypes import *


__secrets = import_dot_folder(".secrets", "clownkey")


def main() -> str:
    try:
        # Start the key manager handling.
        f_wrapper.init(__secrets.init)
        # Start Flet engine and UI.
        f_wrapper.init(ui.ft.app, ui.init)  # type: ignore[reportUnknownArgumentType]
    except:
        return EnvStates.environment_error
    finally:
        results: str = f_wrapper.func_results
        logger.debug(
            f"Results: {results if results != '{}' else EnvStates.unknown_value}"
        )

    return EnvStates.success


if __name__ == "__main__":
    end_status = f_wrapper.init(main).status
    logger.debug(f"{friendly.func_info(main)}, returned: {end_status}")
