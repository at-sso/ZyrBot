Refactored UI and added Markdown support

**Body:**

- Organized UI code: Moved interface-related files to `src/ui` and refactored `src/ui/interface.py` for improved structure and readability.
- Added Markdown rendering (WIP): Implemented basic Markdown parsing (`test.py` & `md_formatter.py`) - not yet integrated into the main program.
- Improved code organization: Moved `command_handler.py` & `function_wrapper.py` to `src/helpers` for better structure.
- Introduced new type `ControlList` for use in the Markdown renderer.
