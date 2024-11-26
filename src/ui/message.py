from enum import Enum

from src.env import *


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
