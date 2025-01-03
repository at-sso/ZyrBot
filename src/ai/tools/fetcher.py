from bs4 import BeautifulSoup
from pathlib import Path
from icecream import ic
import requests
from requests import Session, Response
from requests.exceptions import RequestException
from readability import Document
from lxml_html_clean.clean import Cleaner
from tenacity import retry, stop_after_attempt, wait_fixed

from .exc import *
from src.env import *


def _no_internet(url: str) -> NoReturn:
    """
    Raise an exception indicating that fetching content from the given URL is unsuccessful
    due to connectivity issues or other reasons.

    @param url (str): The URL that failed to fetch.
    @return FetchUnsuccessfulOrImpossible: Custom exception to signal the failure.
    """
    raise FetchUnsuccessfulOrImpossible(f"Error fetching the content from: {url}")


class PythonFetch:
    """
    A class for fetching and processing Python documentation content based on specified versions
    and document modes. It handles retries, cleans HTML content, and saves it as temporary files.
    """

    def __init__(self) -> None:
        """
        Initializes the PythonFetch instance with available Python versions and documentation modes.
        """
        self.__docs_url: LitStr = "https://docs.python.org/"
        """Constant. This is the Python official documentation."""
        self.__doc_type: FlexibleStringMap = {
            "help": ["appetite.html", "interpreter.html", "introduction.html"],
            "controlflow": "controlflow.html",
            "datastructures": "datastructures.html",
            "modules": "modules.html",
        }
        """Supported documents."""
        self.PY_VERSIONS: StringList = self.__get_py_vers()
        """The list of every Python version available."""
        self.DOCUMENT_LIST: StringList = list(self.__doc_type.keys())
        """The list of supported documents."""

    def fetch_content(self, docs_type: str, py_ver: str) -> RawHTMLData:
        """
        Fetch the content of a specified Python documentation section for a specific version.

        @param docs_type (str): The documentation type to fetch (e.g., "help", "controlflow").
        @param py_ver (str): The Python version (e.g., "3.9") for which the documentation is required.

        @return KeyValues: A list of tuples containing fetched content and filenames or a single filename.

        Raises:
            `ValueError`: If the specified Python version (`py_ver`) or `mode` is invalid.
            `DocumentModeIsInvalid`: If the specified mode is not available in `__doc_type`.
        """
        friendly.i_was_called(self.fetch_content)

        # Prepare the 'documents'
        doc_type: FlexibleStringData = self.__doc_type.get(docs_type, None)
        if doc_type is None:
            raise DocumentModeIsInvalid(
                f"Selected mode: '{docs_type}' is an invalid document type."
            )
        logger.info(doc_type)

        # Check if `py_ver` is valid.
        if py_ver not in self.PY_VERSIONS:
            raise ValueError(f"Invalid version: '{py_ver}'")

        # Build the URL
        url: str = f"{self.__docs_url}{py_ver}/tutorial"

        results: RawHTMLFileList = []
        logger.debug(url)
        if isinstance(doc_type, list):
            for doc in doc_type:
                results.append(self.__fetcher(f"{url}/{doc}"))
            return results
        # else, is instance of str.
        return self.__fetcher(f"{url}/{doc_type}")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def __get_response(self, session: Session, url: str) -> Response:
        """
        Send a GET request to the specified URL using a session, with retry logic.

        @param session (Session): The requests session object to use for the request.
        @param url (str): The URL to fetch.

        @return Response: The response object for the GET request.

        Exceptions are not handled within this scope.
        """
        friendly.i_was_called(self.__get_response)
        ic(session, url)
        with session.get(url, timeout=flags.connectTimeout) as response:
            response.raise_for_status()
            return response

    def __fetcher(self, url: str) -> RawHTMLFile:
        """
        Fetch content from a given URL, process it using Readability, and save the content to a file.

        @param url (str): The URL to fetch content from.
        @return KeyValueTuple: A tuple containing the cleaned content and filename.

        Raises:
            `RequestException`: If the request fails due to connectivity issues.
        """
        friendly.i_was_called(self.__fetcher)
        logger.debug(url)

        html_content: Any = object()
        html_raw_text: str = ""
        filename: str = ""
        filepath: Path = Path()

        try:
            with requests.Session() as session:
                response: Response = self.__get_response(session, url)

            # Process the content with Readability
            doc: Document = Document(response.text)
            # Page title
            title: str = doc.title()
            # Simplified "reader mode" HTML
            html_content: Any = doc.summary()

            # Further clean the content using `lxml_html_clean`, we don't want trash!
            cleaner = Cleaner(page_structure=True, safe_attrs_only=True)
            html_content = cleaner.clean_html(html_content)

            # We save the data as a temporal file (not implemented here)
            filename = title.replace(" ", "") + ".html"
            filepath = Path(CACHE_FOLDER) / filename

            # Create the file if it doesn't exists, then open it.
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(html_content)
            logger.debug(f"Content saved to '{filename}'.")

            # Remove every HTML element
            soup = BeautifulSoup(html_content, "html.parser")
            html_raw_text = soup.get_text().strip().replace("\n\n", "\n")

        except RequestException:
            _no_internet(url)
        except Exception:
            logger.critical(
                "An unresolved error occurred.", UnresolvedErrorWhileFetching
            )

        return html_raw_text, filepath

    def __get_py_vers(self) -> StringList | NoReturn:
        """
        Fetch and extract available Python versions from the Python API.

        @return StringList: A sorted list of available Python versions (major.minor).

        Raises:
            `ValueError`: If an invalid version string is encountered.
            `RequestException`: If the request to the Python API fails.
        """
        friendly.i_was_called(self.__get_py_vers)

        PYTHON_API: LitStr = "https://www.python.org/api/v2/downloads/release/"
        versions: set[Any] = set()

        try:
            with requests.Session() as session:
                response: Response = self.__get_response(session, PYTHON_API)

            data: list[GenericKeyMap] = response.json()  # GET JSON request.
            logger.warning("LOADING PYTHON VERSIONS")
            # Extract Python versions into the list.
            for r in data:
                if r["name"].startswith("Python 3.") and not r["pre_release"]:
                    logger.info(f"Trying to fix {r['name']}.")

                    # Find the first occurrence of "3."
                    start: int = r["name"].find("3.")
                    if start == -1:
                        raise ValueError(f"Invalid version string for: {r['name']}.")

                    # Extract the substring starting from "3."
                    ver_substr: str = r["name"][start:]

                    # Split the substring by '.' and take the first two parts
                    major_minor: str = ".".join(ver_substr.split(".")[:2])
                    versions.add(major_minor)
            logger.info("Python versions loaded successfully.")

        except RequestException:
            _no_internet(PYTHON_API)

        return sorted(versions)


py_fetch = PythonFetch()
