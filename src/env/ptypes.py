from pathlib import Path
from PIL.ImageFile import ImageFile
from google.generativeai.types.generation_types import GenerateContentResponse
from collections.abc import (
    Callable,
    Iterable,
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
    Self,
    Type,
    Sized,
)

# Type constructors:
_P = ParamSpec("_P")
_R = TypeVar("_R", bound=Any)
_Media = str | ImageFile


class CallableConstructor(Generic[_P, _R]):
    def __init__(self, func: Callable[_P, _R]) -> None:
        self.func = func

    def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _R:
        return self.func(*args, **kwargs)


# Callables
GenericCallable = Callable[..., Any]
StringCallback = Callable[[Optional[str]], None]

# Lists
GenericList = list[Any]
StringList = list[str]
MediaList = list[_Media]


# Maps
GenericMap = dict[Any, Any]
GenericKeyMap = dict[str, Any]
StringMap = dict[str, str]
NestedStringMap = dict[str, StringMap]

# Tuple
GenericTuple = tuple[Any, ...]
TupleIntInt = tuple[int, int]

# Custom
ExceptionType = Optional[type[Exception]]
FunctionSignature = tuple[GenericCallable, GenericList, GenericKeyMap]
FunctionSignatureDetails = tuple[str, *FunctionSignature]
NullableContentResponse = Optional[GenerateContentResponse]
MediaElement = _Media | MediaList
MemoryList = list[GenericKeyMap | object]
MaybeRaises = Optional[NoReturn]
FlexibleString = str | list[str]
FlexibleStringMap = dict[str, FlexibleString]
FlexibleStringData = Optional[FlexibleString]
RawHTMLFile = tuple[str, Path]
RawHTMLFileList = list[RawHTMLFile]
RawHTMLData = RawHTMLFileList | RawHTMLFile
