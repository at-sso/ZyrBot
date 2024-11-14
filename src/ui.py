from enum import Enum
import uuid
from icecream import ic
import flet as ft
from flet import Text, Page, ControlEvent, Control

from .env import *
from .command_handler import CommandsHandler


class MessageType(Enum):
    USERNAME = "user_name"
    CHAT = "chat_message"
    LOGIN = "login_message"


class Message:
    def __init__(self, user: str, text: str, type: MessageType) -> None:
        self.user = user
        self.text = text
        self.type = type


def interface_main(page: Page) -> str:
    # Helpers
    _i_was_called = lambda f: friendly.i_was_called(f, log=True)
    """Logs relevant information about every function that is being called."""
    _i_was_called(interface_main)

    user_name = ft.TextField(label="Enter your username.")
    """User name placeholder."""
    chat = ft.Column()
    """Chat list"""
    chat_controls: list[Control] = chat.controls
    """Pointer to `chat.controls`"""
    new_msg = ft.TextField()
    """New message placeholder"""

    _new_text: StringCallback = lambda s: chat_controls.append(Text(s))
    _new_alert_text: StringCallback = lambda s: chat_controls.append(
        Text(s, italic=True, color=ft.colors.BLACK45, size=12)
    )
    """Set a new text into the chat"""
    _cmd_handler = CommandsHandler(page=page, chat=chat)
    """Command handler"""
    _cmd_handler.alert_chat = _new_alert_text

    _user_id: Any = page.client_storage.get("user_id")
    """Retrieve a unique user ID for each session"""
    if not _user_id:
        # Generate a new unique ID
        _user_id = str(uuid.uuid4())
        # Store it in client storage
        page.client_storage.set("user_id", _user_id)

    def on_message(msg: Message) -> None:
        """Handles *literally* the entire chat."""
        _i_was_called(on_message)
        _: str = f"{msg.user}: {msg.text}"
        logger.info(f"{msg.type} | {msg.text}")
        if msg.type == MessageType.CHAT:
            _new_text(_)
        elif msg.type == MessageType.LOGIN:
            _new_alert_text(msg.text)
        page.update()

    def send_click(e: ControlEvent) -> None:
        """Send button function, this function also handles possible commands."""
        _i_was_called(send_click)
        msg_text: str = new_msg.value.strip()  # type: ignore[reportOptionalMemberAccess]

        if _cmd_handler.is_a_command(msg_text):
            val = _cmd_handler.execute(msg_text).status
            ic(val)
            if val == EnvStates.exit_on_command:
                # TODO
                logger.warning("Exit on command was called!", NotImplementedError)
            else:
                val()  # type: ignore[reportCallIssue]

        page.pubsub.send_all(
            Message(
                user=page.session.get(MessageType.USERNAME.value),  # type: ignore[reportArgumentType]
                text=new_msg.value,  # type: ignore[reportArgumentType]
                type=MessageType.CHAT,
            )
        )
        new_msg.value = ""
        page.update()

    def join_click(e: ControlEvent) -> None:
        """Join chat interaction, this handles the username generally."""
        _i_was_called(join_click)
        if not user_name.value:
            user_name.error_text = "Your username cannot be blank!"
            user_name.update()
        else:
            page.session.set(MessageType.USERNAME.value, user_name.value)
            page.dialog.open = False  # type: ignore
            page.pubsub.send_all(
                Message(
                    user=user_name.value,
                    text=f"{user_name.value} has joined the chat.",
                    type=MessageType.LOGIN,
                )
            )
            page.update()

    logger.info("Initializing UI.")

    page.pubsub.subscribe(on_message)
    page.dialog = ft.AlertDialog(
        open=True,
        modal=True,
        title=Text("Hello!"),
        content=ft.Column([user_name], tight=True),
        actions=[ft.ElevatedButton(text="Join chat", on_click=join_click)],
        actions_alignment="end",  # type: ignore[reportArgumentType]
    )
    page.add(
        chat,
        ft.Row(controls=[new_msg, ft.ElevatedButton(text="Send", on_click=send_click)]),
    )

    return EnvStates.success.value
