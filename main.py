import src.ui as ui
from src.ui import pyg, win_height
from src.sentiment_data import sia
from src.env import tools
from src.env.ctypes import SIAScoreType
from src.env.logger import *

# Initialize font
font = pyg.font.Font(None, 36)

# UI elements
input_box = pyg.Rect(50, win_height - 100, 400, 40)
button_box = pyg.Rect(500, win_height - 100, 200, 40)
view_stack_button = pyg.Rect(750, win_height - 100, 200, 40)
view_queue_button = pyg.Rect(1000, win_height - 100, 200, 40)

# UI variables
input_text: str = ""
scatter_points: SIAScoreType = sia.get_scores()
scale_offset = 50
y_center: int = win_height // 2

main_loop: bool = True
first_iter: bool = True


def main() -> int:
    global main_loop, input_text, scatter_points, first_iter

    while main_loop:
        ui.window_screen.fill(pyg.Color(ui.BG_COLOR))

        # Draw UI elements using functions from ui.py
        ui.draw_input_box(ui.window_screen, font, input_text, input_box)
        ui.draw_button(ui.window_screen, font, button_box, "Analyze Text")
        ui.draw_button(ui.window_screen, font, view_stack_button, "View Last Score")
        ui.draw_button(ui.window_screen, font, view_queue_button, "View First Score")
        ui.draw_scatter_plot(
            ui.window_screen,
            scatter_points,
            scale_offset,
            y_center,
            ui.win_width,
            win_height,
        )

        # Event handling
        for event in pyg.event.get():
            match event.type:
                case pyg.QUIT:
                    main_loop = False
                case pyg.MOUSEBUTTONDOWN:
                    # Check if Analyze Text button was clicked
                    if button_box.collidepoint(event.pos):
                        sia.add_text(input_text)
                        scatter_points = sia.get_scores()
                        input_text = ""
                    # Check if View Last Score (Stack) button was clicked
                    elif view_stack_button.collidepoint(event.pos):
                        last_score = sia.peek_score_stack()
                        if last_score is not None:
                            logger.debug(f"Last score (Stack): {last_score}")
                    # Check if View First Score (Queue) button was clicked
                    elif view_queue_button.collidepoint(event.pos):
                        first_score = sia.peek_score_queue()
                        if first_score is not None:
                            logger.debug(f"First score (Queue): {first_score}")
                case pyg.KEYDOWN:
                    match event.key:
                        case pyg.K_RETURN:  # Trigger sentiment analysis on Enter press
                            if first_iter:
                                sia.clear_texts()
                                first_iter = False
                            sia.add_text(input_text)
                            scatter_points = sia.get_scores()
                            input_text = ""
                        case pyg.K_s:  # Pop from stack (remove last score)
                            popped_score = sia.pop_score_stack()
                            if popped_score is not None:
                                logger.debug(
                                    f"Popped last score from Stack: {popped_score}"
                                )
                        case pyg.K_q:  # Dequeue from queue (remove first score)
                            dequeued_score = sia.dequeue_score_queue()
                            if dequeued_score is not None:
                                logger.debug(
                                    f"Dequeued first score from Queue: {dequeued_score}"
                                )
                        case pyg.K_l:  # Search linked list for score (demo purposes)
                            try:
                                score = float(input_text)
                                found = sia.search_linked_list(score)
                                logger.debug(
                                    f"Score {score} found in Linked List: {found}"
                                )
                            except ValueError:
                                logger.debug("Invalid score for search.")
                        case pyg.K_d:  # Remove from linked list (remove specific score)
                            try:
                                score = float(input_text)
                                sia.remove_from_linked_list(score)
                                logger.debug(f"Score {score} removed from Linked List")
                            except ValueError:
                                logger.debug("Invalid score for removal.")
                        case pyg.K_BACKSPACE:
                            input_text = input_text[:-1]
                        case _:
                            # Handle text input
                            input_text += event.unicode
                case _:
                    pass

        # Update the display
        pyg.display.flip()
    return 0


if __name__ == "__main__":
    tools.function_handler(main)
