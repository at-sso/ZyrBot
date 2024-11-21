Functional AI Integration & Codebase Improvements

**Body:**

- **AI Functionality Complete (`src/ai/gemini.py`):**
  - Implemented the `GeminiModel` class to retrieve full JSON responses from the Gemini API.
  - Edge cases are handled internally to ensure robustness.
  - Note: Image analysis integration is planned for the future (not currently implemented).
- **Code Refactoring (`src/env/friendly_generics.py` & `src/function_wrapper.py`):**
  - Moved the `__FriendlyLogger` class to its own file named `friendly_generics.py` for better organization.
  - Renamed the class to `__FriendlyGenerics`. Existing access using `friendly` remains unaffected.
  - Modified the `friendly.i_was_called` function to log information by default, streamlining logging calls.
- **Improved Error Handling (`.secrets/clownkey.py`):**
  - Addressed Windows errors related to the `__get_encryption_type` function in `clownkey.py`.
  - As a result, the function was removed.
- **Enhanced Readability (`src/env/friendly_generics.py`):**
  - Renamed functions `list_of_values` and `list_of_generic_values` to `jsonify_values` and `jsonify_generic_values` for improved clarity.
- **New Environment State (`src/env/locales.py`):**
  - Introduced a new environment state: `function_error`.
