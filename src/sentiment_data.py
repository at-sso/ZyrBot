import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from src.env.ctypes import *
from src.env.logger import *


nltk.download("vader_lexicon")


class SIAHandler:
    def __init__(self) -> None:
        self.__analyzer = SentimentIntensityAnalyzer()
        logger.warning("Texts will always be initialized with default data!")
        self.__texts: StrList = [
            "I am extremely happy with the service!",
            "This is terrible, I feel so sad and disappointed.",
            "It's okay, not too bad but not great either.",
            "I love this product, it's amazing!",
            "I don't like it at all.",
        ]
        self.scores: SIAScoreType = self.get_scores()

    def __repr__(self) -> str:
        return f"Data: {self.__load_scores()}"

    def add_text(self, s: str) -> None:
        """Add a new text."""
        # Delete the last value of the list and append the new one.
        if len(self.__texts) > 20:
            self.__texts.pop()
        self.__texts.append(s)
        logger.debug(self.__texts)

    def clear_texts(self) -> None:
        """Clear list of texts."""
        logger.warning("Texts were cleared!")
        self.__texts.clear()

    def get_scores(self) -> SIAScoreType:
        """Get the sentiment score."""
        a: SIAScoreType = self.__load_scores()
        logger.debug(f"List of scores: {a}")
        return a

    def __load_scores(self) -> SIAScoreType:
        """Load directly the scatter plot depending on the `__texts` list values."""
        return [
            self.__analyzer.polarity_scores(text)["compound"] for text in self.__texts
        ]


sia = SIAHandler()
