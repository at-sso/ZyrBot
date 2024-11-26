import flet as ft
from icecream import ic
from src.ui.md_formatter import MarkdownToFletFormatter


def main(page: ft.Page):
    markdown_data = """
# Heading 1
## Heading 2
This is **bold**, this is *italic*, and this is a [link](https://flet.dev).

- Item 1
- Item 2
- Item 3
```
wjat
```
"""

    # Convert Markdown to Flet controls
    f = MarkdownToFletFormatter(markdown_data, ft)
    controls = f.start()

    # Add controls to the page
    page.add(ft.Column(controls, scroll="auto"))


ft.app(target=main)
