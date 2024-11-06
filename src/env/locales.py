from argparse import Action, ArgumentParser, Namespace
import os
import platform
import sys
from icecream import ic
from rich.console import Console
from rich.markdown import Markdown

from .ctypes import *

_abspath: str = os.path.abspath(os.path.dirname(sys.argv[0])).replace("\\", "/")
_enverr: LitStr = "ENVERR"


class __ArgsHandler:
    def __init__(self) -> None:
        global _abspath

        self.__a: Namespace = self.__p()
        """Argument(s)"""
        a = self.__a

        # Global Flags
        self.noWinget: bool = not a.noWinget
        self.devToys: bool = a.devToys
        self.lactoseIntolerant: bool = a.lactoseIntolerant
        # API Key Configuration Flags
        self.doNotSaveMyKey: bool = not a.doNotSaveMyKey
        self.extraSecret: AnyStr = a.extraSecret  # type: ignore[reportGeneralTypeIssues]
        # Logger Configuration Flags
        self.noLogger: bool = a.noLogger
        self.loggerShell: bool = a.loggerShell
        self.noSaveLogger: bool = not a.noSaveLogger
        self.loggerMaxBackup: int = a.loggerMaxBackup
        # UI Configuration Flags
        self.noLoggerInUI: bool = a.noLoggerInUI

        if self.lactoseIntolerant:
            ic.disable()

    def __repr__(self) -> str:
        return f"{self.__a._get_kwargs()}"

    def __p(self) -> Namespace:
        """Parser"""
        global _abspath

        class MarkdownFormatter(Action):
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
            prog="ZyrChatBot", description="Runtime flags.", add_help=False
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
        set_arg("-extraSecret", type=str, default=_enverr)
        # Logger Configuration Flags
        set_arg("-noLogger", action="store_true", default=False)
        set_arg("-loggerShell", action="store_true", default=False)
        set_arg("-noSaveLogger", action="store_true", default=False)
        set_arg("-loggerMaxBackup", type=int, default=5)
        # UI Configuration Flags
        set_arg("-noLoggerInUI", action="store_false", default=True)

        return parser.parse_args()


flags = __ArgsHandler()


class EnvInfo:
    current_path: str = _abspath
    system: str = platform.system()
    release: str = platform.release()
    architecture: tuple[str, str] = platform.architecture()
    compiler: str = platform.python_compiler()

    def __repr__(self) -> str:
        return f"{self.current_path}, {self.system}, {self.release}, {self.architecture}, {self.compiler}"


class EnvStates:
    environment_error: LitStr = _enverr
    unknown_type: LitStr = "?TYPE"


ic(__ArgsHandler())
ic(EnvInfo())
