import traceback as tb
from time import time as timer

from .env.locales import EnvStates

from .env.ptypes import *
from .env.logger import logger as _logger, friendly as _friendly


class __FunctionWrapper:
    def __init__(self) -> None:
        self.status: object = None
        """Holds the value of the executed function."""
        self.func_results: str = str()
        """Get the results of every single executed function at any point."""
        self.__func_results_helper: GenericKeyMap = {}
        """Helper map that stores the name and status of every function."""

    def handler(
        self,
        f: GenericCallable,
        reraise: bool = True,
        *args: object,
        **kwargs: object,
    ) -> Self:
        """Wraps a function call with logging and exception handling.

        This function takes another function (`f`) as an argument and executes it
        within a monitored context. Here's what happens:

        - Start Time Logging:
            - Captures the current time.
            - Logs a message using indicating the start of the wrapped function with its
            details obtained.

        - Function Execution:
            - Attempts to call the provided function `f` and stores the return value
            in `func_val`.

        - Exception Handling:
            - If an exception occurs during `f` execution:
                - Formats a final message using.
                - Logs a critical message using with details about the exception,
                including the function information and the traceback.
                - Re-raises the exception to propagate it further.

        - Normal Execution:
            - If no exception occurs:
                - Formats a final message.
        """
        # Sets the start of the timer.
        start: float = 0.0
        # Sets the end of the timer
        finish: Callable[[], float] = lambda: abs(start - timer())
        # Function duration placeholder
        duration: float = 0.0
        # Function information placeholder
        func_name: str = _friendly.func_info(f)

        _logger.info(f"Start of: {func_name}.")
        try:
            # Start the timer and execute the given callable.
            start = timer()
            func_val: Any = f(*args, **kwargs)
        except:
            # In case of exception, end the timer and log information.
            duration = finish()
            _logger.critical(
                f"Unhandled exception raised in {func_name}; this operation took {duration}. Tb:\n{tb.format_exc()}"
            )
            # If `reraise` is `True`, re-raise the exception that occurred in `f` after logging the tb.
            if reraise:
                raise
            # If `reraise` is `False`, simply set status as an error.
            self.status = EnvStates.environment_error.value
            return self

        # In case of success (no exceptions) finish the timer, and log information.
        duration = finish()
        _logger.info(f"Operation {func_name}, took: {duration}.")

        self.status = func_val
        return self

    def init(
        self,
        f: GenericCallable,
        *args: Any,
        **kwargs: Any,
    ) -> Self:
        """
        Initializes the wrapper, executes the given function with logging and
        exception handling, and updates the results tracker.

        This method wraps the provided function `f`, executing it with the given
        positional and keyword arguments (`args` and `kwargs`). It logs the function
        execution, handles any exceptions, and updates a results dictionary that
        associates each function's descriptive information (`func_info`) with its
        execution status. The function status is retrieved via `self.handler` and
        stored in a formatted JSON string.

        @param f (GenericCallable): The function to be executed.
        @param *args: Positional arguments for the function.
        @param **kwargs: Keyword arguments for the function.

        @return Self: The `__FunctionWrapper` instance, containing the updated function results in JSON format.

        - Process:
            1. Retrieves `func_info` using `_friendly.func_info`, a unique identifier
               for the function based on its signature or properties.
            2. Calls `self.handler` to execute `f` with provided arguments while
               managing exceptions, logging start and end times, and returning a
               `func_results` object.
            3. Checks `func_results.status`:
                - If successful, assigns `EnvStates.success` if `status` is `None`.
                - If execution fails, assigns `EnvStates.unknown_value`.
            4. Populates `self.__func_results_helper` with `func_info` and its status.
            5. Converts `__func_results_helper` to a JSON-formatted string and
               stores it in `self.func_results`.

        """
        # Execute the function with exception handling and logging, capture results
        a = self.handler(f, reraise=False, *args, **kwargs)

        # Store the helper dictionary as a JSON-formatted string in `func_results`
        self.func_results = _friendly.list_of_values(
            self.__func_results_helper, a.status, EnvStates.unknown_value.value, f
        )

        return self


f_wrapper = __FunctionWrapper()
