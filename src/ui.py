import flet as ft

from .env.logger import logger
from .env.locales import EnvInfo


class Message:
    def __init__(self, user: str, text: str):
        self.user = user
        self.text = text


def init(page: ft.Page):
    logger.info("Starting the UI.")

    page.title = EnvInfo.program_name
    chat = ft.Column()
    new_message = ft.TextField()

    def on_message(message: Message):
        chat.controls.append(ft.Text(f"{message.user}: {message.text}"))
        page.update()

    page.pubsub.subscribe(on_message)

    def send_click(e):
        page.pubsub.send_all(Message(user=page.session_id, text=new_message.value))
        new_message.value = ""
        page.update()

    page.add(
        chat, ft.Row([new_message, ft.ElevatedButton("Send", on_click=send_click)])
    )
