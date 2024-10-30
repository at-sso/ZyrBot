import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from src.env.ctypes import *
from src.env.logger import *
from src.data_analyzer_helper import *

nltk.download("vader_lexicon")


class SIAHandler:
    def __init__(self) -> None:
        self.__analyzer: SentimentIntensityAnalyzer = SentimentIntensityAnalyzer()
        logger.warning("Texts will always be initialized with default data!")
        self.feelings_list_limit: int = 20
        self.feelings_list: StrList = [
            "I am extremely happy with the service!",
            "This is terrible, I feel so sad and disappointed.",
            "It's okay, not too bad but not great either.",
            "I love this product, it's amazing!",
            "I don't like it at all.",
        ]
        self.scores: SIAScoreType = self.get_scores()

        # Initializing LinearDataStructure (as Stack and Queue) and LinkedList
        self.score_stack: LinearDataStructure = LinearDataStructure(mode="stack")
        self.score_queue: LinearDataStructure = LinearDataStructure(mode="queue")
        self.custom_linked_list: LinkedList = LinkedList()

    def __repr__(self) -> str:
        return f"Data: {self.__load_scores()}"

    def add_text(self, s: str) -> None:
        """Add a new text."""
        if len(self.feelings_list) >= self.feelings_list_limit:
            logger.warning(f"Limit of {self.feelings_list_limit} was reached.")
            self.feelings_list.pop()
        self.feelings_list.append(s)
        logger.debug(self.feelings_list)

        # Push to Stack and Enqueue to Queue
        score: float = self.__analyzer.polarity_scores(s)["compound"]
        self.score_stack.add(score)
        self.score_queue.add(score)
        self.custom_linked_list.append(score)

    def clear_texts(self) -> None:
        """Clear list of texts."""
        logger.warning("Texts were cleared!")
        self.feelings_list.clear()

    def get_scores(self) -> SIAScoreType:
        """Get the sentiment score."""
        a: SIAScoreType = self.__load_scores()
        logger.debug(f"List of scores: {a}")
        return a

    def __load_scores(self) -> SIAScoreType:
        return [
            self.__analyzer.polarity_scores(text)["compound"]
            for text in self.feelings_list
        ]

    # Stack Operations
    def pop_score_stack(self) -> Optional[Union[str, float]]:
        return self.score_stack.remove() if not self.score_stack.is_empty() else None

    def peek_score_stack(self) -> Optional[Union[str, float]]:
        return self.score_stack.peek() if not self.score_stack.is_empty() else None

    # Queue Operations
    def dequeue_score_queue(self) -> Optional[Union[str, float]]:
        return self.score_queue.remove() if not self.score_queue.is_empty() else None

    def peek_score_queue(self) -> Optional[Union[str, float]]:
        return self.score_queue.peek() if not self.score_queue.is_empty() else None

    # Linked List Operations
    def search_linked_list(self, score: float) -> bool:
        return self.custom_linked_list.search(score)

    def remove_from_linked_list(self, score: float) -> None:
        self.custom_linked_list.remove(score)


sia = SIAHandler()
