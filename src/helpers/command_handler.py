from flet import Page, ListView, Text
from icecream import ic

from src.env import *
from .function_wrapper import f_wrapper


class CommandsHandler:
    def __init__(self, page: Page, chat: ListView) -> None:
        self.page = page
        self.chat = chat

        self.alert_chat: Optional[StringCallback] = None
        self.starter: LitStr = "/"
        self.__handler: dict[str, GenericCallable] = {
            "exit": lambda: EnvStates.exit_on_command,
            "clear": lambda: self.__clear,
            "logchat": lambda: self.__logchat,
        }

        logger.info(f"Setting up '{friendly.full_name(CommandsHandler)}'")
        for key in list(self.__handler):
            self.__handler[f"{self.starter}{key}"] = self.__handler[key]
            del self.__handler[key]
        logger.debug(self.__handler.keys())

    def is_a_command(self, command: str) -> bool:
        """check if the command starts with 'self.starter'."""
        # handler = self.__handler.get(command, self)
        # ic(handler)

        # If `handler` is not equal to `self` and starts with `starter`
        # if not handler is self and :
        #    return True

        return (
            command.startswith(self.starter)
            and self.__handler.get(command, None) is not None
        )

    def execute(self, command: str):
        handler = self.__handler.get(command, None)
        ic(handler)

        # Execute the handler if it is valid, otherwise raise an exception
        if handler == None:
            raise RuntimeError(f"The command {command} is not valid!")
        return f_wrapper.init(handler)

    def __new_message_alert(self, s: str) -> None:
        if not self.alert_chat is None:
            return self.alert_chat(s)  # type: ignore[reportOptionalCall]
        logger.warning(friendly.i_was_called(self.__new_message_alert))

    def __clear(self) -> None:
        self.chat.controls.clear()
        self.__new_message_alert("Chat cleared!")

    def __logchat(self) -> None:
        _: str = "Log chat was used!"
        for val in self.chat.controls:
            # Only log values from the `Text` class
            if isinstance(val, Text):
                chat_val: Optional[str] = val.value
                _ += f"\n{str(chat_val) if chat_val is None else chat_val}"
            # else, do nothing and continue.
        logger.debug(_)
        logger.warning("Cleared messages won't be logged.")
