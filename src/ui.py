from enum import Enum
from icecream import ic
import flet as ft
from flet import Text, Page, ControlEvent, Control

from .env import *
from .command_handler import CommandsHandler

_i_was_called = lambda f: friendly.i_was_called(f, log=True)
"""Logs relevant information about every function that is being called."""


class MessageType(Enum):
    USERNAME = "user_name"
    CHAT = "chat_message"
    LOGIN = "login_message"


class Message:
    def __init__(
        self, user: Optional[str], text: Optional[str], type: MessageType
    ) -> None:
        self.user = user
        self.text = text
        self.msg_type = type


class Interface:
    def __init__(self, page: Page) -> None:
        _i_was_called(self.__init__)
        self.__page = page

        self.__user_name = ft.TextField(label="Enter your username.")
        """User name placeholder."""
        self.__chat = ft.Column()
        """Chat list"""
        self.__chat_controls: list[Control] = self.__chat.controls
        """Pointer to `chat.controls`"""
        self.__new_msg = ft.TextField()
        """New message placeholder"""

        self.__new_text: StringCallback = lambda s: self.__chat_controls.append(Text(s))
        """Adds a new text into the chat"""
        self.__new_alert_text: StringCallback = lambda s: self.__chat_controls.append(
            Text(s, italic=True, color=ft.colors.BLACK45, size=12)
        )
        """Adds an alert text into the chat"""

        self.__cmd_handler = CommandsHandler(page=self.__page, chat=self.__chat)
        """Commands handler"""

        self.__message_manager: dict[MessageType, Callable[[Message], None]] = {
            MessageType.CHAT: lambda M: self.__new_text(f"{M.user}: {M.text}"),
            MessageType.LOGIN: lambda M: self.__new_alert_text(M.text),
        }
        """
        Get the direct type of any message by using the message enum type itself. This directly affects
        the entire chat, so keep that in mind.
        Simply pass a reference `Message` class to this, and it will format everything for you.
        """

        self.start()

    def start(self) -> EnvStates:
        _i_was_called(self.start)

        logger.info("Initializing UI.")

        # Set flet's alert chat to the local instance of the alert chat
        self.__cmd_handler.alert_chat = self.__new_alert_text

        self.__page.pubsub.subscribe(self.__add_new_message)
        self.__page.dialog = ft.AlertDialog(
            open=True,
            modal=True,
            title=Text("Hello!"),
            content=ft.Column([self.__user_name], tight=True),
            actions=[
                ft.ElevatedButton(text="Join chat", on_click=self.__join_chat_event)
            ],
            actions_alignment="end",  # type: ignore[reportArgumentType]
        )
        self.__page.add(
            self.__chat,
            ft.Row(
                controls=[
                    self.__new_msg,
                    ft.ElevatedButton(text="Send", on_click=self.__send_new_message),
                ]
            ),
        )

        return EnvStates.success

    def __add_new_message(self, msg: Message) -> None:
        """Adds a new message to the chat."""
        _i_was_called(self.__add_new_message)
        logger.info(f"{msg.msg_type} | {msg.text}")
        self.__message_manager[msg.msg_type](msg)
        self.__page.update()

    def __send_new_message(self, e: ControlEvent) -> None:
        """Send request function, this function also handles possible commands."""
        _i_was_called(self.__send_new_message)
        message_text: str = self.__new_msg.value.strip()  # type: ignore[reportOptionalMemberAccess]
        # Make `val` a 'global' instance in this scope
        val = object()
        is_command: bool = False

        if self.__cmd_handler.is_a_command(message_text):
            is_command = True

            # Try to get the callable `status` from the command
            try:
                val = self.__cmd_handler.execute(message_text).status
            except:
                # The command doesn't exist, prompt a 'personal' message where the user can see the valid commands
                pass  # TODO
            ic(val)

            # Check if the user wants to exit, otherwise, simply execute the valid command.
            if val == EnvStates.exit_on_command:
                # TODO
                logger.warning("Exit on command was called!", NotImplementedError)
            else:
                val()  # type: ignore[reportCallIssue]

        if not is_command:
            # In case the message wasn't a command, simply prompt the new message into the chat.
            self.__page.pubsub.send_all(
                Message(
                    user=self.__page.session.get(MessageType.USERNAME.value),
                    text=self.__new_msg.value,
                    type=MessageType.CHAT,
                )
            )
        self.__new_msg.value = ""
        self.__page.update()

    def __join_chat_event(self, e: ControlEvent) -> None:
        """Join chat interaction, this handles the username generally."""
        _i_was_called(self.__join_chat_event)
        if not self.__user_name.value:
            self.__user_name.error_text = "Your username cannot be blank!"
            self.__user_name.update()
        else:
            self.__page.session.set(MessageType.USERNAME.value, self.__user_name.value)
            self.__page.dialog.open = False  # type: ignore[reportAttributeAccessIssue]
            self.__page.pubsub.send_all(
                Message(
                    user=self.__user_name.value,
                    text=f"{self.__user_name.value} has joined the chat.",
                    type=MessageType.LOGIN,
                )
            )
            self.__page.update()
