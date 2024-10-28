from pygame import (
    Surface,
    Rect,
)
from pygame.font import Font
from collections.abc import (
    Callable,
)
from typing import (
    Any,
    Generic,
    TypeVar,
)
from typing_extensions import (
    ParamSpec,
    LiteralString as LitStr,
)

List = list
Dict = dict
Tuple = tuple
Type = type

# Type constructors:
_P = ParamSpec("_P")
_R = TypeVar("_R", bound=Any)


class CallableConstructor(Generic[_P, _R]):
    def __init__(self, func: Callable[_P, _R]) -> None:
        self.func = func

    def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _R:
        return self.func(*args, **kwargs)


# Callables
GenericCallable = Callable[..., Any]

# Lists
GenericList = List[Any]
StrList = list[str]

# Maps
GenericMap = Dict[Any, Any]

# Tuple
GenericTuple = tuple[Any, ...]
__TupleIntInt = tuple[int, int]

# Custom
# PyGame
HEXColorType = LitStr
"""The string must represent a 24-bit wise hexadecimal value."""
ScreenSizeType = __TupleIntInt
PosType = __TupleIntInt
ObjectPosType = list[PosType]
# SIA
SIAScoreType = list[float]