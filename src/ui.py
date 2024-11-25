from enum import Enum
import json
from icecream import ic
import flet as ft
from flet import Text, Page, ControlEvent, Control, Dropdown

from .ai.tools.fetcher import py_fetch
from .ai import *
from .ai.gemini import GeminiModel
from .ai import gemini
from .env import *
from .command_handler import CommandsHandler


class DropdownMenuTypes(Enum):
    AI_TYPE = 1
    PY_VERS = 2
    DOCS = 3


dd_menu_t = DropdownMenuTypes


class MessageType(Enum):
    USERNAME = "user_name"
    CHAT = "chat_message"
    ALERT = "alert_message"


class Message:
    def __init__(
        self, user: Optional[str], text: Optional[str], type: MessageType
    ) -> None:
        self.username = user
        self.message = text
        self.msg_type = type


class Interface:
    def __init__(self, page: Page) -> None:
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
            MessageType.ALERT: lambda M: self.__new_alert_text(M.message),
        }
        """
        Get the direct type of any message by using the message enum type itself. This directly affects
        the entire chat, so keep that in mind.
        Simply pass a reference `Message` class to this, and it will format everything for you.
        """

        logger.info("Building dropdown menu lists")
        self.__ai_types_list: StringList = [
            f"Gemini Model: {v}" for v in gemini.ModelNames
        ]
        """Simply allows the user to specify their AI. This can be easily expanded."""
        self.__py_vers: StringList = [f"Python {v}" for v in py_fetch.PY_VERSIONS]
        """The specific Python version, this is used for URL building."""
        self.__doc_list: StringList = [
            f"'{d.capitalize()}' Documents" for d in py_fetch.DOCUMENT_LIST
        ]
        """Allows the AI to have very precise data."""

        self.__dropdown_menu_holders: dict[DropdownMenuTypes, Optional[str]] = {
            dd_menu_t.AI_TYPE: None,
            dd_menu_t.PY_VERS: None,
            dd_menu_t.DOCS: None,
        }
        """
        Get or modify every value from the expected dropdown menus.
        Use the name of the variable as a string key.
        """
        self.__raw_html_data: Optional[RawHTMLData] = None
        self.__gemini: Optional[GeminiModel] = None
        self.__is_after_fetch: bool = False

        self.start()

    def start(self) -> EnvStates:
        friendly.i_was_called(self.start)

        logger.info("Initializing UI.")

        # Set Flet's alert chat to the local instance of the alert chat
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

        ai_types: Dropdown = self.__add_new_dropdown_menu(
            self.__ai_types_list, dd_menu_t.AI_TYPE, "AI type"
        )
        py_vers: Dropdown = self.__add_new_dropdown_menu(
            self.__py_vers, dd_menu_t.PY_VERS, "Python version"
        )
        doc_list: Dropdown = self.__add_new_dropdown_menu(
            self.__doc_list, dd_menu_t.DOCS, "Document type"
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

    def __send_normal_message(self, usr: str, txt: str = EnvStates.unknown_value.value):
        self.__page.pubsub.send_all(
            Message(
                user=usr,
                text=txt,
                type=MessageType.CHAT,
            )
        )

    def __send_alert_message(
        self, usr: str = "", txt: str = EnvStates.unknown_value.value
    ):
        self.__page.pubsub.send_all(
            Message(
                user=usr,
                text=txt,
                type=MessageType.ALERT,
            )
        )

    def __add_new_message_event(self, msg: Message) -> None:
        """Adds a new message to the chat."""
        friendly.i_was_called(self.__add_new_message_event)
        logger.info(f"{msg.msg_type} | {msg.message}")
        self.__message_manager[msg.msg_type](msg)
        self.__page.update()

    def __send_new_message_event(self, e: ControlEvent) -> None:
        """Send message event, this function also handles possible commands."""
        friendly.i_was_called(self.__send_new_message_event)
        message_text: str = self.__write_msg_field.value.strip()  # type: ignore[reportOptionalMemberAccess]
        # Make `val` a 'global' instance in this scope
        val: Optional[object] = object()
        is_command: bool = False
        # If there was any invalid event before this was called, clear the `error_text` event.
        self.__write_msg_field.error_text = ""

        ic(message_text)

        if message_text == "":
            self.__write_msg_field.error_text = "Please write a message before sending."
            self.__write_msg_field.update()
            return

        if self.__cmd_handler.is_a_command(message_text):
            # Try to get the callable `status` from the command
            try:
                is_command = True
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
            self.__send_normal_message(MessageType.USERNAME.value, message_text)
            if self.__is_after_fetch:
                self.__get_new_message_from_ai(message_text)
            else:
                raise gemini.AIRequestFailure(
                    "Cannot send a message to the AI before fetching."
                )

        self.__write_msg_field.value = ""
        self.__page.update()

    def __get_new_message_from_ai(self, user_message: str) -> None:
        friendly.i_was_called(self.__get_new_message_from_ai)

        if self.__gemini is None and not self.__is_after_fetch:
            raise gemini.AIRequestFailure("Failed to get message from AI.")

        if isinstance(self.__raw_html_data, list):
            raise NotImplementedError()
        # The data is a tuple.
        logger.info([user_message, EnvStates.success.value])
        message: StringList = [
            f"Following this documentation:{self.__raw_html_data}",
            f"Answer this:{user_message}",
        ]
        ai_response = self.__gemini.get_response(["".join(message)])
        json_response: GenericKeyMap = json.loads(ai_response.read_text())
        final_response: str = self.__gemini.get_final_response(json_response)

        self.__send_normal_message(EnvInfo.ai_name.value, final_response)

    def __join_chat_event(self, e: ControlEvent) -> None:
        """Join chat interaction, this handles the username generally."""
        friendly.i_was_called(self.__join_chat_event)
        if not self.__get_user_name_field.value:
            self.__get_user_name_field.error_text = "Your username cannot be blank!"
            self.__get_user_name_field.update()
        else:
            self.__page.session.set(
                MessageType.USERNAME.value, self.__get_user_name_field.value
            )
            self.__page.dialog.open = False  # type: ignore[reportAttributeAccessIssue]
            self.__send_alert_message(
                self.__get_user_name_field.value,
                f"{self.__get_user_name_field.value} has joined the chat.",
            )
            self.__page.update()

    def __add_new_dropdown_menu(
        self, options: StringList, key_name: DropdownMenuTypes, preview: LitStr
    ) -> Dropdown:
        """
        options is the list of values, while key_name is expected to be a key from `__dropdown_menu_holder`
        """

        def _(e: ControlEvent) -> None:
            return self.__setup_selected_dropdown_value(key_name, e.control.value)  # type: ignore[reportUnknownArgumentType]

        return ft.Dropdown(
            value=preview,
            options=[ft.dropdown.Option(option) for option in options],
            on_change=_,
        )

    def __setup_selected_dropdown_value(
        self, key_name: DropdownMenuTypes, value: str
    ) -> None:
        friendly.i_was_called(self.__setup_selected_dropdown_value)
        logger.debug(f"{key_name}: {value}")

        # There is no need to check if the key exists since we are enforcing types.
        self.__dropdown_menu_holders[key_name] = value

        # Interact with the selected AI.
        if key_name == dd_menu_t.AI_TYPE:
            name = self.__dropdown_menu_holders.get(dd_menu_t.AI_TYPE)
            logger.debug(f"{dd_menu_t.AI_TYPE.name}: {name}")

            final: str = (
                f"Message {EnvInfo.ai_name.value}{f' - {name}' if name is not None else ''}"
            )
            self.__gemini = GeminiModel(
                self.__get_logical_value(name, gemini.ModelNames)
            )
            self.__write_msg_field.label = final
            self.__write_msg_field.update()

        logger.debug(friendly.iter_info(self.__dropdown_menu_holders))

    def __get_logical_value(self, s: str, l: StringList) -> str:
        """Returns the actual logical value of the dropdown menus"""

        def longest_common_substring(s1: str, s2: str) -> str:
            # Use a sliding window approach for efficiency
            max_len: int = 0
            result: str = ""
            len1, len2 = len(s1), len(s2)
            s1, s2 = s1.lower(), s2.lower()
            dp: list[list[int]] = [[0] * (len2 + 1) for _ in range(len1 + 1)]

            for i in range(1, len1 + 1):
                for j in range(1, len2 + 1):
                    if s1[i - 1] == s2[j - 1]:
                        dp[i][j] = dp[i - 1][j - 1] + 1
                        if dp[i][j] > max_len:
                            max_len = dp[i][j]
                            result = s1[i - max_len : i]

            return result

        max_common: str = ""
        for s2 in l:
            common: str = longest_common_substring(s, s2)
            if len(common) > len(max_common):
                max_common = common

        return max_common

    def __check_if_fetching_is_possible(self, e: ControlEvent) -> None:
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

            aim: str = self.__dropdown_menu_holders[dd_menu_t.AI_TYPE]  # type: ignore[reportAssignmentType]
            ver: str = self.__get_logical_value(
                self.__dropdown_menu_holders[dd_menu_t.PY_VERS],
                py_fetch.PY_VERSIONS,
            )
            doc: str = self.__get_logical_value(
                self.__dropdown_menu_holders[dd_menu_t.DOCS],
                py_fetch.DOCUMENT_LIST,
            )

            ic(aim, ver, doc)
            self.__raw_html_data = py_fetch.fetch_content(doc, ver)
            self.__is_after_fetch = True

            self.__send_alert_message(
                txt=f"Selected {aim}, with Python {ver} & {doc.capitalize()}."
            )
            self.__page.update()
