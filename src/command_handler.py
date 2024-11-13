from flet import Page, Column
from icecream import ic

from .env import *
from .function_wrapper import f_wrapper


class CommandsHandler:
    def __init__(self, page: Page, chat: Column) -> None:
        self.page = page
        self.chat = chat

        self.alert_chat: Optional[StringCallback] = None
        self.__starter: LitStr = "/"
        self.__handler: dict[str, GenericCallable] = {
            "exit": lambda: EnvStates.exit_on_command,
            "clear": lambda: self.__clear,
        }

        logger.info(f"Setting up '{friendly.full_name(CommandsHandler)}'")
        for key in list(self.__handler):
            self.__handler[f"{self.__starter}{key}"] = self.__handler[key]
            del self.__handler[key]
        logger.debug(self.__handler.keys())

    def is_a_command(self, command: str) -> bool:
        _ = self.__handler.get(command, self)
        ic(_)
        if not _ is self and command.startswith(self.__starter):
            return True
        return False

    def execute(self, command: str):
        _ = self.__handler.get(command, lambda: False)
        ic(_)
        return f_wrapper.init(_)

    def __new_message_alert(self, s: str) -> None:
        if not self.alert_chat is None:
            return self.alert_chat(s)  # type: ignore[reportOptionalCall]
        logger.warning(friendly.i_was_called(self.__new_message_alert))

    def __clear(self) -> None:
        self.chat.controls.clear()
        self.__new_message_alert("Chat cleared!")
