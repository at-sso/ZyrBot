Fixed AI Model Setting Issue

**Body:**

- Fixed user error when setting the AI model.
- Made `GEMINI_MODEL_NAMES` public for developer customization (previously static in `gemini.py`).
- Updated `GeminiModel`'s `model` argument to be optional (string or `None`).
  - Allows setting the model later.
  - Raises `AIModelIsInvalid` if `model` is `NoneType` and `do_raise` is `True` (default).
- Removed optional typing for `self.__gemini` due to model change.
