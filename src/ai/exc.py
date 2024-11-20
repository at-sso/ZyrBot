from ..env import *


class FriendlyNameIsInvalid(BaseException):
    def __init__(self, s: object) -> None:
        super().__init__(s, self.__class__)


class ImpossibleKeyRetrieval(BaseException):
    def __init__(self, s: object) -> None:
        super().__init__(s, self.__class__)


class AIRequestFailure(BaseException):
    def __init__(self, s: object) -> None:
        super().__init__(s, self.__class__)


class InvalidAIRequestFormat(BaseException):
    def __init__(self, s: object) -> None:
        super().__init__(s, self.__class__)
