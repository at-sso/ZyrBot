__all__ = ["logger", "friendly"]

import os
import json
import logging
import traceback
from icecream import ic
from enum import Enum

from .locales import EnvStates, flags
from .ptypes import *
from .globales import *


class __LoggerHandler:
    def __init__(self) -> None:
        """
        The function initializes a logger with a specified log file and logs a message indicating the
        logger has started.
        """
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.__logger_function: dict[int, Callable[[object], None]] = {
            logging.DEBUG: lambda x: self.logger.debug(x),
            logging.INFO: lambda x: self.logger.info(x),
            logging.WARNING: lambda x: self.logger.warning(x),
            logging.ERROR: lambda x: self.logger.error(x),
            logging.CRITICAL: lambda x: self.logger.critical(x),
        }

        self.logger.setLevel(logging.DEBUG)

        if flags.noSaveLogger:
            # Ensure the directory exists
            logger_directory: str = os.path.dirname(LOGGER_FILE)
            if not os.path.exists(logger_directory):
                os.makedirs(logger_directory)

        # Delete the oldest files.
        try:
            files: list[str] = os.listdir(LOGGER_FOLDER_PATH)
            if not len(files) < LOGGER_MAX_BACKUP:
                logger_amount: int = max(len(files) // LOGGER_MAX_BACKUP, 1)
                logs_to_delete: list[str] = files[
                    : len(LOGGER_FOLDER_PATH) - logger_amount
                ]
                ic(logs_to_delete)
                for file_name in logs_to_delete:
                    file_path: str = os.path.join(LOGGER_FOLDER_PATH, file_name)
                    os.remove(file_path)
        # If `os.remove` fails, it's likely due to file permissions or non-existence.
        # Since file deletion is not essential for this operation, we can safely ignore exceptions.
        except:
            pass

        if flags.noSaveLogger:
            # Create a file handler
            logger_handler = logging.FileHandler(LOGGER_FILE, mode="w")
            # Create a formatter and set the formatter for the handler
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )
            logger_handler.setFormatter(formatter)
            # Add the handler to the logger
            self.logger.addHandler(logger_handler)

            self.handler(logging.INFO, "Logger started.")
            self.handler(logging.DEBUG, f"Max logger backup: {LOGGER_MAX_BACKUP}.")

    def handler(
        self, logging_level: int, message: object, exc: ExceptionType = Exception
    ) -> None:
        """
        The function `__logger_message_handler` calls a specified function with a given argument.

        @param logging_level The expected to be a callable that takes a single argument of type `object` and returns `None`.
        @param msg The `msg` parameter in the `__logger_message_handler` function is an object that
        represents the message or information that will be passed to the `logging_func` function for logging
        purposes.
        """
        if flags.noLogger:
            return

        if flags.loggerShell:
            print(logging.getLevelName(logging_level) + " |", message)
        self.__logger_function[logging_level](message)

        if exc != Exception:
            raise exc(message)


_hdlr = __LoggerHandler()


class __Logger:
    def debug(self, message: object) -> None:
        """
        The function `debug` logs a debug message using a logger message handler.

        @param message The `message` parameter in the `debug` method is an object that represents the
        message to be logged at the 'DEBUG' level.
        """
        _hdlr.handler(logging.DEBUG, message)

    def info(self, message: object) -> None:
        """
        This function logs an informational message using a logger message handler.

        @param message The `message` parameter in the `info` method is an object that represents the
        message to be logged at the 'INFO' level.
        """
        _hdlr.handler(logging.INFO, message)

    def warning(self, message: object, exc: ExceptionType = Exception) -> None:
        """
        The `warning` function logs a warning message using a logger message handler.

        @param message The `message` parameter in the `info` warning is a string that represents the
        message to be logged at the 'WARNING' level.
        """
        _hdlr.handler(logging.WARNING, message, exc)

    def error(self, message: object, exc: ExceptionType = Exception) -> None:
        """
        The function `error` logs an error message using a logger message handler.

        @param message The `message` parameter in the `error` method is an object that represents the
        message to be logged at the 'ERROR' level.
        @param exc Allows you to force an exception of any type besides the base class 'Exception'.
        """
        _hdlr.handler(logging.ERROR, message, exc)

    def critical(self, message: object, exc: ExceptionType = Exception) -> None:
        """
        This function logs a critical message using a logger message handler.

        @param message The `message` parameter in the `critical` method is an object that represents the
        message to be logged at the 'CRITICAL' level.
        @param exc Allows you to force an exception of any type besides the base class 'Exception'.
        """
        _hdlr.handler(logging.CRITICAL, message, exc)


logger = __Logger()
"""
This instance is used for logging messages at different levels such as debug, 
info, warning, error, and critical.
"""


def _custom_serializer(obj: Any) -> Any | str:
    # Handle enums and other non-serializable objects
    if isinstance(obj, Enum):
        return obj.value
    elif hasattr(obj, "__dict__"):
        return __FriendlyLogger.full_name(obj)
    return str(obj)  # Default to string representation


class __FriendlyLogger:
    @staticmethod
    def var_type(v: object) -> str:
        """
        Determines the type of a variable.

        @param x: The variable whose type is to be determined.
        @return: The name of the type as a string.
        """
        return f"({type(v).__name__})"

    @staticmethod
    def unique_id(v: object) -> str:
        """
        Generates a unique identifier string for a given variable.

        @param x: The variable to generate the identifier for.
        @return: A string representing the unique memory address of the variable.
        """
        return f"id: {id(v)}"

    @staticmethod
    def full_name(x: object, err: str = EnvStates.unknown_location.value) -> str:
        """
        Gets the fully qualified name of a callable or variable.

        @param x: The callable or variable.
        @param err (optional): Error name.
        @return: The fully qualified name or `err` if the qualified name is unknown.
        """
        try:
            return f"{x.__module__}.{x.__qualname__}"
        except AttributeError:
            return err

    def var_info(self, v: object) -> str:
        """
        Provides detailed information about a variable including its type, class, and unique identifier.

        @param f: The variable to analyze.
        @return: A string with the full name, type, and unique identifier of the variable.
        """
        return f"{self.full_name(v)}, {self.var_type(v)}, {self.unique_id(v)}"

    def func_info(self, f: GenericCallable) -> str:
        """
        Provides detailed information about a callable including its class and unique identifier.

        @param f: The callable to analyze.
        @return: A string with the full name and unique identifier of the callable.
        """
        return f"{self.full_name(f, f.__name__)}, {self.unique_id(f)}"

    @staticmethod
    def map_keys(d: GenericMap) -> str:
        """
        Returns a string representation of all keys in a dictionary.

        @param d: The dictionary to retrieve keys from.
        @return: A string list of all keys.
        """
        return f"{list(d.keys())}"

    @staticmethod
    def map_items(d: GenericMap) -> str:
        """
        Returns a string representation of all key-value pairs in a dictionary.

        @param d: The dictionary to retrieve items from.
        @return: A string list of all key-value pairs.
        """
        return f"{list(d.items())}"

    @staticmethod
    def get_map_key_item(d: GenericMap, key: object) -> str:
        """
        Retrieves the value associated with a key in a dictionary and formats it as a string.

        Returns "BADVALUE" if the key is not found.

        @param d: The dictionary to search.
        @param key: The key to look for.
        @return: A formatted string of the key-value pair or "BADVALUE".
        """
        err = EnvStates.unknown_value.value
        item = d.get(key, err)
        if item == err:
            return err
        return f"<{key}: {item}>"

    def get_key_from_item(self, d: GenericMap, item: object) -> str:
        """
        Searches for a given item in a dictionary and retrieves its key.

        This method can be slow because it involves reversing the dictionary search.
        Returns "BADVALUE" if the item is not found.

        @param d: The dictionary to search.
        @param item: The item to search for.
        @return: The key associated with the item or "BADVALUE".
        """
        # Create a reversed dictionary to map items back to keys
        reversed_dict = {value: key for key, value in d.items()}
        return self.get_map_key_item(reversed_dict, item)

    def iter_info(self, it: Iterable[object]) -> str:
        """Show the iterator type and the contents. The contents are formatted to be readable and friendly."""
        content = [self.var_info(item) for item in it]
        return f"Iterable {self.var_type(it)} = {content}"

    def list_of_values(
        self,
        content: GenericKeyMap,
        given_var: object,
        err: object,
        *args: object,
    ) -> str:
        """
        Populates the `content` dictionary with the status of each variable or callable in `args`.

        This function iterates over a list of variables or callables (`args`) and assigns each
        a corresponding status in the `content` dictionary based on its value:
            - If the variable is `None`, it is assigned `EnvStates.success`.
            - If the variable matches the provided `err` value, it is assigned `EnvStates.unknown_value`.
            - Otherwise, the variable's own value is stored as its status.

        @param content (GenericKeyMap): A dictionary to store the statuses of variables or callables.
        @param err (object): A value representing an error state. If a variable in `args` matches this value, it is assigned `EnvStates.unknown_value`.
        @param *args (object): A list of variables or callable functions whose statuses will be stored in `content`.

        Returns:
            str: A JSON-formatted string representing the `content` dictionary, with the statuses of each variable.
        """
        for var in args:
            name: str = self.var_info(var)
            if given_var is None:
                # If the function returned None, assign EnvStates.success as default
                content[name] = EnvStates.success.value
            elif given_var == err:
                # Explicitly set to unknown value if an error occurs
                content[name] = EnvStates.unknown_value.value
            else:
                # For all other cases, store the status as is
                content[name] = given_var

        # Get the formatted results in JSON.
        return json.dumps(content, indent=4, default=_custom_serializer)

    def list_of_generic_values(self, *args: object) -> str:
        _: GenericKeyMap = {}
        for var in args:
            name: str = f"{self.var_type(var)}, {self.unique_id(var)}"
            _[name] = str(var)
        return json.dumps(_, indent=4, default=_custom_serializer)

    def i_was_called(self, f: GenericCallable, log: bool = False) -> str:
        """
        Returns a string representation of a callable being called.

        @param f: The callable to analyze.
        @param log: Allows this function to log at level 'INFO' the returned message.
        @return: A string with the full name and unique identifier of the callable being called.
        """
        _: str = f"Callable '{self.full_name(f, f.__name__)}' was called."
        if log:
            logger.info(_)
        return _


friendly = __FriendlyLogger()
"""Provide user-friendly string representations for various values."""
