from collections.abc import (
    Callable,
)
from typing import (
    Any,
    Generic,
    TypeVar,
    Optional,
)
from typing_extensions import (
    AnyStr,
    ParamSpec,
    LiteralString as LitStr,
    NoReturn,
)

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
GenericList = list[Any]
StrList = list[str]

# Maps
GenericMap = dict[Any, Any]

# Tuple
GenericTuple = tuple[Any, ...]
TupleIntInt = tuple[int, int]

# Custom
ExceptionType = type[Exception]
JSONType = dict[str, Any]
