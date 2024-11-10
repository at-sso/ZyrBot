import sys
import traceback as tb
import importlib.util as import_util
from importlib.machinery import ModuleSpec
from pathlib import Path
from time import time as timer
from types import ModuleType

from .locales import EnvStates

from .ctypes import *
from .logger import logger as _logger, friendly as _friendly


class __FunctionWrapper:
    def __init__(self) -> None:
        self.name: object = None
        self.fstatus: object = None

    def init(
        self,
        func: GenericCallable,
        reraise: bool = True,
        *args: object,
        **kwargs: object,
    ) -> Self:
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
        # Sets the start of the timer.
        start: float = 0.0
        # Sets the end of the timer
        finish: Callable[[], float] = lambda: abs(start - timer())
        # Function duration placeholder
        duration: float = 0.0
        # Function information placeholder
        func_name: str = _friendly.func_info(func)

        _logger.info(f"Start of: {func_name}.")

        try:
            start = timer()
            func_val: Any = func(*args, **kwargs)
        except:
            duration = finish()
            _logger.critical(
                f"Unhandled exception raised in {func_name}; this operation took {duration}. Tb: \n{tb.format_exc()}"
            )
            if reraise:
                raise
            self.fstatus = EnvStates.environment_error
            return self
        finally:
            self.name = _friendly.full_name(func)

        duration = finish()
        _logger.info(f"Operation {func_name}, took: {duration}.")

        self.fstatus = func_val
        return self


f_wrapper = __FunctionWrapper()


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
