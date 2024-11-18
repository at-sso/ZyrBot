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
        self.username = user
        self.message = text
        self.msg_type = type


class Interface:
    def __init__(self, page: Page) -> None:
        _i_was_called(self.__init__)
        self.__page = page

        self.__get_user_name_field = ft.TextField(label="Enter your username.")
        """User name field"""
        self.__new_msg_field = ft.TextField(
            label="Message <AI_TYPE>",
            hint_text="Write a message.",
            autofocus=True,
            shift_enter=True,
            min_lines=1,
            max_lines=10,
            filled=True,
            expand=True,
            on_submit=self.__send_new_message_event,
        )
        """New message text field"""

        self.__chat = ft.ListView(expand=True, spacing=10, auto_scroll=True)
        """Chat list"""
        self.__chat_ctrl_ref: list[Control] = self.__chat.controls
        """Pointer to `chat.controls`"""

        self.__new_text: StringCallback = lambda s: self.__chat_ctrl_ref.append(Text(s))
        """Adds a new text into the chat"""
        self.__new_alert_text: StringCallback = lambda s: self.__chat_ctrl_ref.append(
            Text(s, italic=True, color=ft.colors.BLACK45, size=12)
        )
        """Adds an alert text into the chat"""

        self.__cmd_handler = CommandsHandler(page=self.__page, chat=self.__chat)
        """Commands handler"""

        self.__message_manager: dict[MessageType, Callable[[Message], None]] = {
            MessageType.CHAT: lambda M: self.__new_text(f"{M.username}: {M.message}"),
            MessageType.LOGIN: lambda M: self.__new_alert_text(M.message),
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

        self.__page.pubsub.subscribe(self.__add_new_message_event)

        self.__page.dialog = ft.AlertDialog(
            open=True,
            modal=True,
            title=Text("Hello!"),
            content=ft.Column([self.__get_user_name_field], tight=True),
            actions=[
                ft.ElevatedButton(text="Join chat", on_click=self.__join_chat_event)
            ],
            actions_alignment="end",  # type: ignore[reportArgumentType]
        )

        self.__page.add(
            ft.Container(
                content=self.__chat,
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=5,
                padding=10,
                expand=True,
            ),
            ft.Row(
                controls=[
                    self.__new_msg_field,
                    ft.IconButton(
                        icon=ft.icons.SEND_ROUNDED,
                        tooltip="Send message",
                        on_click=self.__send_new_message_event,
                    ),
                ]
            ),
        )

        return EnvStates.success

    def __add_new_message_event(self, msg: Message) -> None:
        """Adds a new message to the chat."""
        _i_was_called(self.__add_new_message_event)
        logger.info(f"{msg.msg_type} | {msg.message}")
        self.__message_manager[msg.msg_type](msg)
        self.__page.update()

    def __send_new_message_event(self, e: ControlEvent) -> None:
        """Send message event, this function also handles possible commands."""
        _i_was_called(self.__send_new_message_event)
        message_text: str = self.__new_msg_field.value.strip()  # type: ignore[reportOptionalMemberAccess]
        # Make `val` a 'global' instance in this scope
        val: Optional[object] = object()
        is_command: bool = False
        # If there was any invalid event before this was called, clear the `error_text` event.
        self.__new_msg_field.error_text = ""

        ic(message_text)

        if message_text == "":
            self.__new_msg_field.error_text = "Please write a message before sending."
            self.__new_msg_field.update()
            return

        if self.__cmd_handler.is_a_command(message_text):
            # Try to get the callable `status` from the command
            try:
                is_command = True
                val = self.__cmd_handler.execute(message_text).status
                logger.debug(f"Command {message_text} exists.")
            except:
                # The command doesn't exist, prompt a message so the user can see the valid commands.
                self.__new_msg_field.error_text = (
                    f"The command '{message_text}' doesn't exists. "
                    "Please use '/help' to see a list of available commands."
                )
                self.__new_msg_field.update()
                # Log information, and set the `val` variable to `None` to avoid exceptions and overlap.
                logger.warning(f"Command {message_text} does not exists.")
                val = None
            finally:
                ic(val, is_command)

            # Check if the user wants to exit, otherwise, simply execute the valid command.
            if val == EnvStates.exit_on_command:
                # TODO
                logger.warning("Exit on command was called!", NotImplementedError)
            elif val != None:
                val()  # type: ignore[reportCallIssue]

        if not is_command:
            # In case the message wasn't a command, simply prompt the new message into the chat.
            self.__page.pubsub.send_all(
                Message(
                    user=self.__page.session.get(MessageType.USERNAME.value),
                    text=self.__new_msg_field.value,
                    type=MessageType.CHAT,
                )
            )
        self.__new_msg_field.value = ""
        self.__page.update()

    def __join_chat_event(self, e: ControlEvent) -> None:
        """Join chat interaction, this handles the username generally."""
        _i_was_called(self.__join_chat_event)
        if not self.__get_user_name_field.value:
            self.__get_user_name_field.error_text = "Your username cannot be blank!"
            self.__get_user_name_field.update()
        else:
            self.__page.session.set(
                MessageType.USERNAME.value, self.__get_user_name_field.value
            )
            self.__page.dialog.open = False  # type: ignore[reportAttributeAccessIssue]
            self.__page.pubsub.send_all(
                Message(
                    user=self.__get_user_name_field.value,
                    text=f"{self.__get_user_name_field.value} has joined the chat.",
                    type=MessageType.LOGIN,
                )
            )
            self.__page.update()
