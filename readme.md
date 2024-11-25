AI Integration & UI Enhancements

**Body:**

- **Major Feature:** Implemented AI functionality with documentation fetching and rendering in the UI.
- **UI Enhancements:** Added functionalities for fetching documentation based on user queries and displaying AI responses. (`src/ui.py`)
- **Documentation Fetching:**
  - Integrated BeautifulSoup in `fetcher.py` for HTML text extraction.
  - Introduced `ModelNames` in `gemini.py` for API interaction.
  - Implemented JSON handling in `gemini.py` and `ui.py` for storing and retrieving responses.
  - Added a new exception `UnresolvedErrorWhileFetching` for error handling in `fetcher.py`.
- **Code Improvements:**
  - Removed unnecessary imports across various files (`main.py`, `gemini.py`).
  - Fixed the `full_name` function in `friendly_generics.py` to accurately display names.
  - Improved type definitions in `ptypes.py` by renaming and restructuring types related to HTML data.
