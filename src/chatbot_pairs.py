from .env.ctypes import *

pairs: list[list[Any]] = [
    [r"(hi|hello|hey)", ["Hello!", "Hi there!", "Hey!"]],
    [r"my name is (.*)", ["Nice to meet you, %1! How are you?"]],
    [
        r"what is your name?",
        ["I don't have a name, my creator doesn't really like me."],
    ],
    [r"how are you?", ["I'm doing well, thank you!", "I'm great!"]],
    [r"sorry (.*)", ["No problem!", "It's okay!", "No worries!"]],
    [r"(quit|exit)", ["Goodbye! Have a nice day!"]],
    # Fallback response (Not a paired answer)
    [
        r"(.*)",
        [
            "I'm not sure I understand that.",
            "Could you rephrase?",
            "Sorry, I didn't get that.",
        ],
    ],
]
