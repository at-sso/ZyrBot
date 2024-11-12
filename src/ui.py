import flet as ft

from .env.ptypes import *
from .env.locales import *
from .env.logger import *


class UserInterface:
    def __init__(self, page: ft.Page) -> None:
        """
        Initializes the ChatApp with the main page and sets up the initial UI elements.
        """
        self.page = page
        self.user_name: Any = None

        logger.info("Initializing UI.")
        # Set up the page properties
        self.page.title = EnvInfo.program_name.value
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.scroll = ft.ScrollMode.AUTO

        # Initialize the message display area and input controls
        self.message_display = ft.Column(scroll=ft.ScrollMode.AUTO)
        self.message_input = ft.TextField(
            hint_text="Enter message", expand=True, on_submit=self.send_message
        )
        self.send_button = ft.IconButton(icon=ft.icons.SEND, on_click=self.send_message)

        # Display the username prompt dialog at the start of the program
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Enter your username"),
            content=ft.TextField(on_submit=self.set_user_name),
            actions=[ft.TextButton("Submit", on_click=self.set_user_name)],
        )
        self.page.dialog.open = True
        self.page.update()

    def set_user_name(self, e: Any = None) -> None:
        """
        Sets the user's name based on input and initializes the main chat UI.

        @param e: Event that triggered the function (optional). Used to retrieve the entered username.
        """
        # Get the user's input from the dialog
        self.user_name = e.control if e else None
        if self.user_name:
            # Close the dialog and initialize the main chat area
            self.page.dialog.open = False
            self.page.add(
                self.message_display, ft.Row([self.message_input, self.send_button])
            )
            self.page.update()

    def send_message(self, e: Any = None) -> None:
        """
        Handles sending a message from the user and generating an AI response.

        @param e: Event that triggered the function (optional).
        """
        user_message = self.message_input.value.strip()
        if user_message:
            # Display the user's message in the chat display area
            self.add_message(self.user_name, user_message)

            # Get the AI response and display it
            ai_response = self.get_ai_response(user_message)
            self.add_message(EnvInfo.ai_name.value, ai_response)

            # Clear the input field for the next message
            self.message_input.value = ""
            self.page.update()

    def add_message(self, sender: str, message: str) -> None:
        """
        Adds a message bubble to the chat display area with the sender's name and message.

        @param sender (str): The name of the message sender (e.g., "User" or "AI").
        @param message (str): The text content of the message to display.
        """
        # Format and add a row with the sender's name and message text
        self.message_display.controls.append(
            ft.Row([ft.Text(sender, weight=ft.FontWeight.BOLD), ft.Text(message)])
        )

    def get_ai_response(self, user_message: str) -> str:
        """
        Generates a response from the AI to the user's message. Not yet implemented.

        @param user_message (str): The message from the user that the AI should respond to.
        @param str: The AI's response message.
        """
        # Placeholder for AI response logic - TODO: Replace this with real AI response in the future
        return "NotImplementedError"  # AI response generation not yet implemented
