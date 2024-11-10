import json
import stat

from src import ui
from src.env import *
from src.env.ctypes import *


__secrets = import_dot_folder(".secrets", "clownkey")


class FormatResults:
    def __init__(self) -> None:
        # Stores function info as a dictionary
        self.function_results: GenericKeyMap = {}

    def init(
        self,
        f: GenericCallable,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        # Populate `function_results` by executing each function with `f_wrapper`
        func_info = friendly.func_info(f)
        wrapped_func = f_wrapper.init(f, False, *args, **kwargs)
        if wrapped_func:
            status = wrapped_func.fstatus
            if status == None:
                self.function_results[func_info] = (
                    status if status != None else EnvStates.success
                )
        else:
            self.function_results[func_info] = EnvStates.unknown_value

    def get(self) -> str:
        """Return a JSON string of the formatted results"""
        return json.dumps(self.function_results, indent=4)


R = FormatResults()
"""Results"""


def main() -> str:
    try:
        # Start the key manager handling.
        R.init(__secrets.init)
        # Start Flet engine and UI.
        R.init(ui.ft.app, ui.init)  # type: ignore[reportUnknownArgumentType]
    except:
        return EnvStates.environment_error
    finally:
        results: str = R.get()
        logger.debug(
            f"Results: {results if results != '{}' else EnvStates.unknown_value}"
        )

    return EnvStates.success


if __name__ == "__main__":
    end_status = f_wrapper.init(main).fstatus
    logger.debug(f"{friendly.func_info(main)}, returned: {end_status}")
