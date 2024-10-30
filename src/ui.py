__all__ = [
    "pyg",
    "win_width",
    "win_height",
    "BG_COLOR",
    "NEUTRAL_LINE_COLOR",
    "SENTIMENT_SCORE_COLOR",
    "TEXT_COLOR",
    "BUTTON_COLOR",
    "INPUT_BOX_COLOR",
    "draw_input_box",
    "draw_button",
    "draw_scatter_plot",
]

import pygame as pyg

from src.env.logger import *
from src.env.ctypes import *

logger.info("Initializing PyGame engine.")
pyg.init()


win_width, win_height = 1024, 768
window_screen: Surface = pyg.display.set_mode((win_width, win_height))
pyg.display.set_caption("Sentiment Analysis")
pyg.display.set_icon(pyg.image.load("./src/.icon.jpg"))

# Colors
BG_COLOR = "#202020"
NEUTRAL_LINE_COLOR = "#FFFFFF"
SENTIMENT_SCORE_COLOR = "#2020FF"
TEXT_COLOR = "#FFFFFF"
BUTTON_COLOR = "#008000"
INPUT_BOX_COLOR = "#323232"


def draw_input_box(
    screen: Surface, font: Font, input_text: str, input_box: Rect
) -> None:
    """Draws the text input box."""
    pyg.draw.rect(screen, pyg.Color(INPUT_BOX_COLOR), input_box)
    input_surface: Surface = font.render(input_text, True, pyg.Color(TEXT_COLOR))
    screen.blit(input_surface, (input_box.x + 10, input_box.y + 5))


def draw_button(screen: Surface, font: Font, button_box: Rect, text: str) -> None:
    """Draws the button to trigger analysis."""
    pyg.draw.rect(screen, pyg.Color(BUTTON_COLOR), button_box)
    button_surface: Surface = font.render(text, True, pyg.Color(TEXT_COLOR))
    screen.blit(button_surface, (button_box.x + 20, button_box.y + 5))


def draw_scatter_plot(
    screen: Surface,
    scatter_points: SIAScoreType,
    scale_offset: int,
    y_center: int,
    width: int,
    height: int,
) -> None:
    """Draws the scatter plot with sentiment scores."""
    x_spacing: int = (width - 2 * scale_offset) // max(1, len(scatter_points) - 1)
    # Neutral line at y=0
    pyg.draw.line(
        screen,
        pyg.Color(NEUTRAL_LINE_COLOR),
        (scale_offset, y_center),
        (width - scale_offset, y_center),
        1,
    )

    # Draw scatter plot points
    for i, score in enumerate(scatter_points):
        x: int = scale_offset + i * x_spacing
        y = int(y_center - score * (height / 2 - scale_offset))
        pyg.draw.circle(screen, pyg.Color(SENTIMENT_SCORE_COLOR), (x, y), 5)


logger.info("Done!")
