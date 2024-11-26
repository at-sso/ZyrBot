from markdown_it import MarkdownIt
from markdown_it.token import Token

from src.env import *


class TokenIsNoneType(BaseException):
    def __init__(self, s: object) -> None:
        super().__init__(s, self.__class__)


_HEADING_OPEN: str = "heading_open"
_PARAGRAPH_OPEN: str = "paragraph_open"
_LIST_ITEM_OPEN: str = "list_item_open"
_FENCE: str = "fence"
_INLINE: str = "inline"


class MarkdownToFletFormatter:
    def __init__(self, markdown: str, ft: ModuleType) -> None:
        __md_it = MarkdownIt()

        self.__md: str = markdown
        """Reference to the `init` parameter `markdown`"""
        self.__md_tokens: list[Token] = __md_it.parse(self.__md)
        """`MarkdownIt.parse` value, following the `markdown` parameter"""
        self.__token: Optional[Token] = None
        """Markdown token holder"""
        self.__ft: ModuleType = ft
        """Expected `flet` package"""
        self.__ft_controls: ControlList = []
        """Reference to `Control`"""
        self.__contents: Optional[str] = None
        """Expected `flet` contents"""

        self.__LOOKUP_CALLABLE: dict[str, GenericCallable] = {
            _INLINE: self.__inline,
            _HEADING_OPEN: self.__heading_open,
            _PARAGRAPH_OPEN: self.__paragraph_open,
            _LIST_ITEM_OPEN: self.__list_item_open,
            _FENCE: self.__fence,
        }

    def start(self) -> ControlList:
        """Parses Markdown and generates a list of Flet controls."""
        friendly.i_was_called(self.start)

        for self.__token in self.__md_tokens:
            final: Optional[GenericCallable] = self.__LOOKUP_CALLABLE.get(
                self.__token.type, None
            )
            if final is None:
                logger.warning(
                    f"The value of '{self.__token.type}' is not equal to any value in: '{self.__LOOKUP_CALLABLE.keys()}'"
                )
                continue
            final()

        return self.__ft_controls

    def __is_token_none(self) -> None:
        if self.__token is None:
            raise TokenIsNoneType("Using invalid token for markdown.")

    def __set_next(self) -> bool:
        inline_token: Optional[Token] = next(
            (
                t
                for t in self.__md_tokens
                if t.type == "inline" and t.map == self.__token.map
            ),
            None,
        )

        if inline_token is None:
            logger.error(f"No matching 'inline' token for map {self.__token.map}")
            return False

        self.__contents = inline_token.content
        return True

    def __inline(self) -> None:
        """Handle inline content like bold, italic, and links."""
        friendly.i_was_called(self.__inline)
        self.__is_token_none()

        if not hasattr(self.__token, "children") or self.__token.children is None:
            logger.warning(f"Inline token {self.__token} has no children.")
            return

        inline_controls: ControlList = []
        for child in self.__token.children:
            match child.type:
                case "text":
                    inline_controls.append(self.__ft.Text(child.content))
                case "strong_open":
                    inline_controls.append(self.__ft.Text(weight="bold"))
                case "em_open":
                    inline_controls.append(self.__ft.Text(italic=True))
                case "link_open":
                    # Extract href from the token attributes
                    href = next(
                        (attr[1] for attr in child.attrs if attr[0] == "href"), "#"
                    )
                    inline_controls.append(
                        self.__ft.Text(
                            f"[{href}]", color=self.__ft.colors.BLUE, italic=True
                        )
                    )
                case _:
                    pass

        self.__ft_controls.extend(inline_controls)

    def __heading_open(self) -> None:
        """Get the heading level (e.g., h1, h2, etc.)"""
        friendly.i_was_called(self.__heading_open)
        self.__is_token_none()

        level = int(self.__token.tag[1])
        if self.__set_next():
            self.__ft_controls.append(
                self.__ft.Text(
                    self.__contents, size=24 - (level - 1) * 2, weight="bold"
                )
            )

    def __paragraph_open(self) -> None:
        """Get paragraph content"""
        friendly.i_was_called(self.__paragraph_open)
        self.__is_token_none()

        if self.__set_next():
            self.__ft_controls.append(self.__ft.Text(self.__contents))

    def __list_item_open(self) -> None:
        """Handle list items"""
        friendly.i_was_called(self.__list_item_open)
        self.__is_token_none()

        if self.__set_next():
            self.__ft_controls.append(self.__ft.Text(f"- {self.__contents}"))

    def __fence(self) -> None:
        """Render code blocks"""
        friendly.i_was_called(self.__fence)
        self.__is_token_none()

        self.__ft_controls.append(
            self.__ft.Container(
                self.__ft.Text(
                    self.__token.content,
                    font_family="Courier New",
                    size=12,
                    color=self.__ft.colors.GREY,
                ),
                padding=10,
                border=self.__ft.border.all(1, self.__ft.colors.GREY),
                border_radius=5,
                bgcolor=self.__ft.colors.BLACK12,
            )
        )
