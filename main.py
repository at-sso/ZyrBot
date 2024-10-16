from nltk.chat.util import Chat, reflections

from src.env import tools
from src.chatbot_pairs import pairs


def main() -> int:
    chatbot = Chat(pairs, reflections)
    tools.clear_terminal()
    print("Hello!")
    chatbot.converse()
    return 0


if __name__ == "__main__":
    tools.function_handler(main)
