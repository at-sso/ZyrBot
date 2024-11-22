Refactored Code & Added Python Documentation Fetching

**Body:**

**Code Organization:**

- **Improved Readability:** Restructured `exc.py` to `src/ai/tools/exc.py` for better local package organization.

**New Features:**

- **Python Documentation Fetching:** Added `src/ai/tools/fetcher.py` for efficient management of Python documentation retrieval. This includes:
  - `PythonFetch` class: Fetches and processes Python documentation content based on versions and document modes (retries, HTML cleaning, temporary file storage).
  - `fetch_content`: Retrieves content for a specific Python documentation section and version.
  - Additional private methods for request handling and content processing.

**Enhancements:**

- **`function_wrapper.py`:** Added `large_data` flag to signal large data in `friendly_generics.jsonify_values`, promoting optimization strategies.
- **`locales.py`:** Removed unnecessary `unknown_type` (explain briefly if context allows).
- **Type Safety:** Introduced the `MaybeRaises` type to indicate potential exceptions in functions. Additional private types.
