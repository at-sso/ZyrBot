Enhanced Security & Documentation

**Body:**

- **Enhanced API Key Security (`src/secrets/clownkey.py`):**
  - Improved the docstring for the `get` function, emphasizing the importance of secure key handling.
  - Modified the default argument for `decrypt` to `False`. Developers are not required to explicitly set it for encryption by default.
- **Improved Code Documentation (`src/env/friendly_generics.py`):**
  - Enhanced docstrings for functions within `friendly_generics.py` for better code clarity.
- **Refined `full_name` Function (`src/env/friendly_generics.py`):**
  - Improved the `full_name` function to check for expected attributes before returning a value.
- **New API Key Validation Test (`main.py`):**
  - Added a small test in `main.py` to verify API key validity using `clownkey.get`.
