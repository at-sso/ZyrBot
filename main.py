import src.ui as ui
from src.ui import pyg
from src.sentiment_data import sia

from src.env import tools
from src.env.ctypes import *

font = pyg.font.Font(None, 36)

# UI elements
input_box = pyg.Rect(50, ui.win_height - 100, 400, 40)
button_box = pyg.Rect(500, ui.win_height - 100, 200, 40)

# UI variables
input_text: str = ""
scatter_points: SIAScoreType = sia.get_scores()
scale_offset = 50
y_center: int = ui.win_height // 2

main_loop: bool = True


def main() -> int:
    global main_loop, input_text, scatter_points

    while main_loop:
        ui.window_screen.fill(pyg.Color(ui.BG_COLOR))

        # Draw UI elements using functions from ui.py
        ui.draw_input_box(ui.window_screen, font, input_text, input_box)
        ui.draw_button(ui.window_screen, font, button_box)
        ui.draw_scatter_plot(
            ui.window_screen,
            scatter_points,
            scale_offset,
            y_center,
            ui.win_height,
            ui.win_height,
        )

        # Event handling
        for event in pyg.event.get():
            match event.type:
                case pyg.QUIT:
                    main_loop = False
                case pyg.MOUSEBUTTONDOWN:
                    # Check if button was clicked
                    if button_box.collidepoint(event.pos):
                        sia.add_text(input_text)
                        scatter_points = sia.get_scores()
                        input_text = ""
                case pyg.KEYDOWN:
                    match event.key:
                        case pyg.K_RETURN:
                            # Trigger sentiment analysis on Enter press
                            sia.add_text(input_text)
                            scatter_points = sia.get_scores()
                            input_text = ""
                        case _:
                            pass
                case _:
                    pass

        # Update the display
        pyg.display.flip()
    return 0


if __name__ == "__main__":
    tools.function_handler(main)
