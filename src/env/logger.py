__all__ = ["logger"]

import os
import logging
from typing import Any
from collections.abc import Callable

from .ctypes import *
from .globales import *


class __LoggerHandler:
    def __init__(self) -> None:
        """
        The function initializes a logger with a specified log file and logs a message indicating the
        logger has started.
        """
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.__logger_function: Dict[int, Callable[[str], None]] = {
            logging.DEBUG: lambda x: self.logger.debug(x),
            logging.INFO: lambda x: self.logger.info(x),
            logging.WARNING: lambda x: self.logger.warning(x),
            logging.ERROR: lambda x: self.logger.error(x),
            logging.CRITICAL: lambda x: self.logger.critical(x),
        }

        self.logger.setLevel(logging.DEBUG)

        # Ensure the directory exists
        logger_directory: str = os.path.dirname(LOGGER_FILE)
        if not os.path.exists(logger_directory):
            os.makedirs(logger_directory)

        # Delete the oldest files.
        try:
            files: List[str] = os.listdir(LOGGER_FOLDER_PATH)
            if not len(files) < LOGGER_MAX_BACKUP:
                logger_amount: int = max(len(files) // LOGGER_MAX_BACKUP, 1)
                files_to_delete: List[str] = files[
                    : len(LOGGER_FOLDER_PATH) - logger_amount
                ]
                for file_name in files_to_delete:
                    file_path: str = os.path.join(LOGGER_FOLDER_PATH, file_name)
                    os.remove(file_path)
        # If `os.remove` fails, it's likely due to file permissions or non-existence.
        # Since file deletion is not essential for this operation, we can safely ignore exceptions.
        except:
            pass
        # Create a file handler
        logger_handler = logging.FileHandler(LOGGER_FILE, mode="w")
        # Create a formatter and set the formatter for the handler
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        logger_handler.setFormatter(formatter)
        # Add the handler to the logger
        self.logger.addHandler(logger_handler)

        self.handler(logging.INFO, "Logger started.")

    def handler(
        self, logging_level: int, message: Any, force_logger_in_shell: bool = False
    ) -> None:
        """
        The function `__logger_message_handler` calls a specified function with a given argument.

        @param logging_level The expected to be a callable that takes a single argument of type `object` and returns `None`.
        @param msg The `msg` parameter in the `__logger_message_handler` function is an object that
        represents the message or information that will be passed to the `logging_func` function for logging
        purposes.
        """
        if not self.logger.disabled:
            if force_logger_in_shell:
                print(logging.getLevelName(logging_level), message)
            self.__logger_function[logging_level](message)


_hdlr = __LoggerHandler()


class __Logger:
    def __init__(self) -> None:
        self.in_shell: bool = False

    def debug(self, message: Any) -> None:
        """
        The function `debug` logs a debug message using a logger message handler.

        @param message The `message` parameter in the `debug` method is an object that represents the
        message to be logged at the 'DEBUG' level.
        """
        _hdlr.handler(logging.DEBUG, message, force_logger_in_shell=self.in_shell)

    def info(self, message: Any) -> None:
        """
        This function logs an informational message using a logger message handler.

        @param message The `message` parameter in the `info` method is an object that represents the
        message to be logged at the 'INFO' level.
        """
        _hdlr.handler(logging.INFO, message, force_logger_in_shell=self.in_shell)

    def warning(self, message: Any) -> None:
        """
        The `warning` function logs a warning message using a logger message handler.

        @param message The `message` parameter in the `info` warning is a string that represents the
        message to be logged at the 'WARNING' level.
        """
        _hdlr.handler(logging.WARNING, message, force_logger_in_shell=self.in_shell)

    def error(self, message: Any) -> None:
        """
        The function `error` logs an error message using a logger message handler.

        @param message The `message` parameter in the `error` method is an object that represents the
        message to be logged at the 'ERROR' level.
        """
        _hdlr.handler(logging.ERROR, message, force_logger_in_shell=self.in_shell)

    def critical(self, message: Any) -> None:
        """
        This function logs a critical message using a logger message handler.

        @param message The `message` parameter in the `critical` method is an object that represents the
        message to be logged at the 'CRITICAL' level.
        """
        _hdlr.handler(logging.CRITICAL, message, force_logger_in_shell=self.in_shell)


logger = __Logger()
"""
This instance is used for logging messages at different levels such as debug, 
info, warning, error, and critical.
"""
