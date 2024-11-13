import os
import platform
import sys
from icecream import ic
from enum import Enum
from datetime import datetime
from rich.console import Console
from rich.markdown import Markdown
from argparse import Action, ArgumentParser, Namespace

from .ptypes import *

_ai_name: LitStr = "Zyr"
_prog_name: str = f"{_ai_name}-ChatBot"
_abspath: str = os.path.abspath(os.path.dirname(sys.argv[0])).replace("\\", "/")
_logger_max: int = 1
"""AKA > 'loggerMaxBackup'"""
_logger_name: str = f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.log"
"""AKA > 'loggerName'"""


class EnvStates(Enum):
    success = "SUCCESS"
    exit_on_command = "CMDEXIT"
    environment_error = "ENVERROR"
    unknown_value = "BADVALUE"
    unknown_type = "BADTYPE"
    unknown_location = "BADLOCATION"


class __ArgsHandler:
    def __init__(self) -> None:
        global _abspath

        self.__a: Namespace = self.__p()
        """Argument(s)"""

        # Global Flags
        self.noWinget: bool = not self.__a.noWinget
        self.devToys: bool = self.__a.devToys
        self.lactoseIntolerant: bool = self.__a.lactoseIntolerant
        # API Key Configuration Flags
        self.doNotSaveMyKey: bool = not self.__a.doNotSaveMyKey
        self.extraSecret: bytes = self.__a.extraSecret.encode("utf-32")
        self.deadInternet: bool = not self.__a.deadInternet
        # Logger Configuration Flags
        self.noLogger: bool = self.__a.noLogger
        self.loggerShell: bool = self.__a.loggerShell
        self.noSaveLogger: bool = not self.__a.noSaveLogger
        self.loggerMaxBackup: int = self.__a.loggerMaxBackup
        self.loggerName: str = self.__a.loggerName
        # UI Configuration Flags
        self.noLoggerInUI: bool = self.__a.noLoggerInUI

        class __Helper:
            is_extraSecrets_set: bool = not (
                self.extraSecret != EnvStates.unknown_value.value.encode("utf-32")
            )
            is_loggerMaxBackup_set: bool = not (self.loggerMaxBackup > _logger_max)
            is_loggerName_set: bool = not (self.loggerName != _logger_name)

        self.help = __Helper()
        """
        Is a flag set...?
        This will not show flags that already boolean values.
        """

        if self.lactoseIntolerant:
            ic.disable()

    def __repr__(self) -> str:
        self.__a.extraSecret = "secrets!"
        return f"{self.__a._get_kwargs()}"

    def __p(self) -> Namespace:
        """Parser"""
        global _abspath

        class MarkdownFormatter(Action):
            # Shout-out chatgpt because I have no idea on how this works
            def __init__(
                self, option_strings, dest, nargs=0, help_file_path=None, **kwargs  # type: ignore
            ) -> None:
                global _abspath
                self.help_file_path: Any = f"{_abspath}/{help_file_path}"
                super().__init__(option_strings, dest, nargs=nargs, **kwargs)  # type: ignore

            def __call__(
                self, parser, namespace, values, option_string=None  # type: ignore
            ) -> NoReturn:
                """Prints and formats markdown text files into the terminal."""
                console = Console()
                with open(self.help_file_path) as help_message:
                    markdown = Markdown(help_message.read())
                console.print(markdown)
                parser.exit()
                exit(0)

        parser = ArgumentParser(
            prog=_prog_name, description="Runtime flags.", add_help=False
        )
        set_arg: Callable[..., Action] = parser.add_argument

        set_arg(
            "-h",
            "-help",
            help="Shows help message.",
            action=MarkdownFormatter,
            help_file_path=f"/docs/.flags.md",
        )

        # Global Flags
        set_arg("-noWinget", action="store_true", default=False)
        set_arg("-devToys", action="store_true", default=False)
        set_arg("-lactoseIntolerant", action="store_true", default=False)
        # API Key Configuration Flags
        set_arg("-doNotSaveMyKey", action="store_true", default=False)
        set_arg("-extraSecret", type=str, default=EnvStates.unknown_value.value)
        set_arg("-deadInternet", action="store_false", default=True)
        # Logger Configuration Flags
        set_arg("-noLogger", action="store_true", default=False)
        set_arg("-loggerShell", action="store_true", default=False)
        set_arg("-noSaveLogger", action="store_true", default=False)
        set_arg("-loggerMaxBackup", type=int, default=_logger_max)
        set_arg("-loggerName", type=str, default=_logger_name)
        # UI Configuration Flags
        set_arg("-noLoggerInUI", action="store_false", default=True)

        return parser.parse_args()


flags = __ArgsHandler()


class EnvInfo(Enum):
    ai_name = _ai_name
    program_name = _prog_name
    current_path = _abspath
    system = platform.system()
    release = platform.release()
    architecture = platform.architecture()
    compiler = platform.python_compiler()


ic(__ArgsHandler())
