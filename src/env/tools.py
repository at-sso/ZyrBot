__all__ = [
    "clear_terminal",
    "f_wrapper",
    "import_dot_folder",
]

import os
import sys
import traceback
import importlib.util as import_util
from importlib.machinery import ModuleSpec
from pathlib import Path
from time import time as timer
from types import ModuleType

from .ctypes import *
from .logger import logger as __logger


def clear_terminal() -> int:
    """clears the terminal screen using platform-dependent commands."""
    return os.system("cls" if os.name == "nt" else "clear")


def f_wrapper(func: GenericCallable) -> Any:
    """Wraps a function call with logging and exception handling.

    This function takes another function (`func`) as an argument and executes it
    within a monitored context. Here's what happens:

    - Start Time Logging:
        - Captures the current time.
        - Logs a message using indicating the start of the wrapped function with its
          details obtained.

    - Function Execution:
        - Attempts to call the provided function `func` and stores the return value
          in `func_val`.

    - Exception Handling:
        - If an exception occurs during `func` execution:
            - Formats a final message using.
            - Logs a critical message using with details about the exception,
            including the function information and the traceback.
            - Re-raises the exception to propagate it further.

    - Normal Execution:
        - If no exception occurs:
            - Formats a final message.

    - Return Value:
        - Returns the value returned by the wrapped function.
    """
    start: float = timer()

    def __format_final_message(func: GenericCallable, is_exception: bool) -> None:
        """
        The function `__format_final_message` logs the execution time of a given function based on the start and
        end timestamps.

        @param func The `func` parameter in the `__format_final_message` function is a callable that represents
        the function being executed. It can be any function that can be called with any number of arguments
        and returns a value of any type.
        """
        duration: float = start - timer()
        __logger.debug(
            f"{'Unhandled operation' if is_exception else 'Operation'}: "
            f"{func} took: {abs(duration)} ms."
        )

    __logger.info(f"Start of: {func}.")

    try:
        func_val: Any = func()
    except Exception:
        __format_final_message(func, is_exception=True)
        __logger.critical(
            f"Unhandled exception raised in {func}:" f"\n{traceback.format_exc()}"
        )
        raise

    __format_final_message(func, is_exception=False)
    return func_val


def import_dot_folder(folder_name: LitStr, module_name: LitStr) -> ModuleType:
    # Locate the .dot folder path
    dot_folder_path: Path = Path(folder_name).resolve()
    module_file: Path = dot_folder_path / f"{module_name}.py"

    if not module_file.is_file():
        raise ModuleNotFoundError(f"No module named '{module_name}' in {folder_name}")

    # Load the module dynamically
    spec: Optional[ModuleSpec] = import_util.spec_from_file_location(
        module_name, module_file
    )
    module: ModuleType = import_util.module_from_spec(spec)  # type: ignore[reportArgumentType]
    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # type: ignore[reportOptionalMemberAccess]

    return module
