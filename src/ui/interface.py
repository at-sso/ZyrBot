import json
from icecream import ic
import flet as ft

from src.ai import *
from src.env import *
from src.helpers import *

from .dropdown_menus import DropdownMenuTypes
from .message import Message, MessageType
from .helper import int_helper


class Interface:
    def __init__(self, page: ft.Page) -> None:
        friendly.i_was_called(self.__init__)
        self.__page = page

        self.__get_user_name_field = ft.TextField(label="Enter your username.")
        """User name field"""
        self.__write_msg_field = ft.TextField(
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

        self.__dropdown_rows = ft.Row()
        self.__chat = ft.ListView(expand=True, spacing=10, auto_scroll=True)
        """Chat list"""
        self.__chat_ctrls: list[ft.Control] = self.__chat.controls
        """Pointer to `chat.controls`"""

        self.__new_text: StringCallback = lambda s: self.__chat_ctrls.append(ft.Text(s))
        """Adds a new text into the chat"""
        self.__new_alert_text: StringCallback = lambda s: self.__chat_ctrls.append(
            ft.Text(s, italic=True, color=ft.colors.BLACK45, size=12)
        )
        """Adds an alert text into the chat"""

        self.__cmd_handler = CommandsHandler(page=self.__page, chat=self.__chat)
        """Commands handler"""

        self.__message_manager: dict[MessageType, Callable[[Message], None]] = {
            MessageType.CHAT: lambda M: self.__new_text(f"{M.username}: {M.message}"),
            MessageType.ALERT: lambda M: self.__new_alert_text(M.message),
        }
        """
        Get the direct type of any message by using the message enum type itself. This directly affects
        the entire chat, so keep that in mind.
        Simply pass a reference `Message` class to this, and it will format everything for you.
        """

        logger.info("Building dropdown menu lists")
        self.__ai_types_list: StringList = [
            f"Gemini Model: {v}" for v in GEMINI_MODEL_NAMES
        ]
        """Simply allows the user to specify their AI. This can be easily expanded."""
        self.__py_vers: StringList = [f"Python {v}" for v in py_fetch.PY_VERSIONS]
        """The specific Python version, this is used for URL building."""
        self.__doc_list: StringList = [
            f"'{d.capitalize()}' Documents" for d in py_fetch.DOCUMENT_LIST
        ]
        """Allows the AI to have very precise data."""

        self.__dropdown_menu_holders: dict[DropdownMenuTypes, Optional[str]] = {
            DropdownMenuTypes.AI_TYPE: None,
            DropdownMenuTypes.PY_VERS: None,
            DropdownMenuTypes.DOCS: None,
        }
        """
        Get or modify every value from the expected dropdown menus.
        Use the name of the variable as a string key.
        """
        self.__raw_html_data: Optional[RawHTMLData] = None
        self.__gemini = GeminiModel(do_raise=False)
        self.__is_after_fetch: bool = False

        self.start()

    def start(self) -> EnvStates:
        friendly.i_was_called(self.start)

        logger.info("Initializing UI.")

        # Set Flet alert chat to the local instance of the alert chat
        self.__cmd_handler.alert_chat = self.__new_alert_text

        self.__page.pubsub.subscribe(self.__handle_new_message)

        self.__page.dialog = ft.AlertDialog(
            open=True,
            modal=True,
            title=ft.Text("Hello!"),
            content=ft.Column([self.__get_user_name_field], tight=True),
            actions=[
                ft.ElevatedButton(
                    text="Join chat", on_click=self.__user_joins_chat_event
                )
            ],
            actions_alignment="end",  # type: ignore[reportArgumentType]
        )

        ai_types: ft.Dropdown = self.__add_new_dropdown_menu(
            self.__ai_types_list, DropdownMenuTypes.AI_TYPE, "AI type"
        )
        py_vers: ft.Dropdown = self.__add_new_dropdown_menu(
            self.__py_vers, DropdownMenuTypes.PY_VERS, "Python version"
        )
        doc_list: ft.Dropdown = self.__add_new_dropdown_menu(
            self.__doc_list, DropdownMenuTypes.DOCS, "Document type"
        )

        self.__dropdown_rows.controls.extend([ai_types, py_vers, doc_list])
        self.__page.add(self.__dropdown_rows)

        self.__page.add(
            ft.Container(
                content=self.__chat,
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=5,
                padding=10,
                expand=True,
            ),
            ft.ElevatedButton(
                text="Fetch",
                on_click=self.__check_if_fetching_is_possible,
                tooltip="Start fetching data.",
            ),
            ft.Row(
                controls=[
                    self.__write_msg_field,
                    ft.IconButton(
                        icon=ft.icons.SEND_ROUNDED,
                        tooltip="Send message",
                        on_click=self.__send_new_message_event,
                    ),
                ]
            ),
        )

        return EnvStates.success

    def __send_normal_msg(
        self, usr: str, txt: str = EnvStates.unknown_value.value
    ) -> None:
        self.__page.pubsub.send_all(
            Message(
                user=usr,
                text=txt,
                type=MessageType.CHAT,
            )
        )

    def __send_alert_msg(
        self, usr: str = "", txt: str = EnvStates.unknown_value.value
    ) -> None:
        self.__page.pubsub.send_all(
            Message(
                user=usr,
                text=txt,
                type=MessageType.ALERT,
            )
        )

    def __handle_new_message(self, msg: Message) -> None:
        """Adds a new message to the chat."""
        friendly.i_was_called(self.__handle_new_message)
        logger.info(f"{msg.msg_type} | {msg.message}")
        self.__message_manager[msg.msg_type](msg)
        self.__page.update()

    def __send_new_message_event(self, e: ft.ControlEvent) -> None:
        """Send new messages into the chat correctly."""
        friendly.i_was_called(self.__send_new_message_event)
        message_text: str = self.__write_msg_field.value.strip()  # type: ignore[reportOptionalMemberAccess]
        # If there was any invalid event before this was called, clear the `error_text` event.
        self.__write_msg_field.error_text = ""

        ic(message_text)

        if message_text == "":
            self.__write_msg_field.error_text = "Please write a message before sending."
            self.__write_msg_field.update()
            return

        if not self.__handle_commands_between_messages(message_text):
            # In case the message wasn't a command, simply prompt the new message into the chat.
            self.__send_normal_msg(MessageType.USERNAME.value, message_text)
            if self.__is_after_fetch:
                self.__get_new_message_from_ai(message_text)
            else:
                raise ai_exc.AIRequestFailure(
                    "Cannot send a message to the AI before fetching."
                )

        self.__write_msg_field.value = ""
        self.__page.update()

    def __user_joins_chat_event(self, e: ft.ControlEvent) -> None:
        """Join chat interaction, this handles the username generally."""
        friendly.i_was_called(self.__user_joins_chat_event)
        if not self.__get_user_name_field.value:
            self.__get_user_name_field.error_text = "Your username cannot be blank!"
            self.__get_user_name_field.update()
        else:
            self.__page.session.set(
                MessageType.USERNAME.value, self.__get_user_name_field.value
            )
            self.__page.dialog.open = False  # type: ignore[reportAttributeAccessIssue]
            self.__send_alert_msg(
                self.__get_user_name_field.value,
                f"{self.__get_user_name_field.value} has joined the chat.",
            )
            self.__page.update()

    def __handle_commands_between_messages(self, message_text: str) -> bool:
        val: Optional[object] = None

        if self.__cmd_handler.is_a_command(message_text):
            # Try to get the callable `status` from the command
            try:
                val = self.__cmd_handler.execute(message_text).status
                logger.debug(f"Command {message_text} exists.")
            except:
                # The command doesn't exist, prompt a message so the user can see the valid commands.
                self.__write_msg_field.error_text = (
                    f"The command '{message_text}' doesn't exists. "
                    "Please use '/help' to see a list of available commands."
                )
                self.__write_msg_field.update()
                # Log information, and set the `val` variable to `None` to avoid exceptions and overlap.
                logger.warning(f"Command {message_text} does not exists.")

                # Always return True if the value was indeed a command,
                # in that way we avoid exceptions in the `if, elif` block.
                return True
            finally:
                ic(val)

            # Check if the user wants to exit, otherwise, simply execute the valid command.
            if val == EnvStates.exit_on_command:
                # TODO
                logger.warning("Exit on command was called!", NotImplementedError)
            elif val != None:
                val()  # type: ignore[reportCallIssue]

            # Always return true if the value was indeed a command.
            return True

        # Argument `message_text` is not a command, simple as that.
        return False

    def __get_new_message_from_ai(self, user_message: str) -> None:
        friendly.i_was_called(self.__get_new_message_from_ai)

        if not self.__is_after_fetch:
            raise ai_exc.AIRequestFailure("Failed to get message from AI.")

        if isinstance(self.__raw_html_data, list):
            raise NotImplementedError()

        # The data is a tuple.
        logger.info([user_message, EnvStates.success.value])
        message: StringList = [
            f"Following this documentation:{self.__raw_html_data}",
            f"Answer this:{user_message}",
        ]
        ai_response: Path = self.__gemini.get_response(["".join(message)])
        json_response: GenericKeyMap = json.loads(ai_response.read_text())
        final_response: str = self.__gemini.get_final_response(json_response)

        self.__send_normal_msg(EnvInfo.ai_name.value, final_response)

    def __add_new_dropdown_menu(
        self, options: StringList, key_name: DropdownMenuTypes, preview: LitStr
    ) -> ft.Dropdown:
        """
        options is the list of values, while key_name is expected to be a key from `__dropdown_menu_holder`
        """
        event: Callable[[ft.ControlEvent], None] = (
            lambda e: self.__setup_selected_dropdown_value(key_name, e.control.value)  # type: ignore
        )

        return ft.Dropdown(
            value=preview,
            options=[ft.dropdown.Option(option) for option in options],
            on_change=event,
        )

    def __setup_selected_dropdown_value(
        self, key_name: DropdownMenuTypes, value: str
    ) -> None:
        friendly.i_was_called(self.__setup_selected_dropdown_value)
        logger.debug(f"{key_name}: {value}")

        # There is no need to check if the key exists since we are enforcing types.
        self.__dropdown_menu_holders[key_name] = value

        # Interact with the selected AI.
        if key_name == DropdownMenuTypes.AI_TYPE:
            name = self.__dropdown_menu_holders.get(DropdownMenuTypes.AI_TYPE)
            logger.debug(f"{DropdownMenuTypes.AI_TYPE.name}: {name}")

            final: str = (
                f"Message {EnvInfo.ai_name.value}{f' - {name}' if name is not None else ''}"
            )
            self.__gemini = GeminiModel(
                int_helper.get_logical_value(name, GEMINI_MODEL_NAMES)
            )
            self.__write_msg_field.label = final
            self.__write_msg_field.update()

        logger.debug(friendly.iter_info(self.__dropdown_menu_holders))

    def __check_if_fetching_is_possible(self, e: ft.ControlEvent) -> None:
        any_is_none: bool = False

        # If any value is True, do not fetch data.
        for k in self.__dropdown_menu_holders.keys():
            logger.debug(k)
            if self.__dropdown_menu_holders[k] is None:
                any_is_none = True

        if any_is_none:
            self.__write_msg_field.error_text = "You must select every value in the dropdown menus to fetch information."
            logger.warning(self.__write_msg_field.error_text)
            self.__write_msg_field.update()
        else:
            self.__write_msg_field.error_text = ""

            aim: str = self.__dropdown_menu_holders[DropdownMenuTypes.AI_TYPE]  # type: ignore[reportAssignmentType]
            ver: str = int_helper.get_logical_value(
                self.__dropdown_menu_holders[DropdownMenuTypes.PY_VERS],
                py_fetch.PY_VERSIONS,
            )
            doc: str = int_helper.get_logical_value(
                self.__dropdown_menu_holders[DropdownMenuTypes.DOCS],
                py_fetch.DOCUMENT_LIST,
            )

            ic(aim, ver, doc)
            self.__raw_html_data = py_fetch.fetch_content(doc, ver)
            self.__is_after_fetch = True

            self.__send_alert_msg(
                txt=f"Selected {aim}, with Python {ver} & {doc.capitalize()}."
            )
            self.__page.update()
