from ..env import *


class FriendlyNameIsInvalid(BaseException):
    def __init__(self, s: object) -> None:
        super().__init__(s, f"{self.__module__}.FriendlyNameIsInvalid")


class ImpossibleKeyRetrieval(BaseException):
    def __init__(self, s: object) -> None:
        super().__init__(s, f"{self.__module__}.ImpossibleKeyRetrieval")
