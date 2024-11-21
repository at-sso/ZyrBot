from typing import Any
import requests
from requests import Response
from readability import Document
from lxml_html_clean.clean import Cleaner


def fetch_reader_mode_content(url: str, save_to_file: bool = True) -> Any | None:
    try:
        # Fetch the web page
        response: Response = requests.get(url)
        # Ensure the request was successful
        response.raise_for_status()

        # Process the content with Readability
        doc = Document(response.text)
        title: str = doc.title()
        # This is the simplified "reader mode" HTML for easier analysis
        content: Any = doc.summary()

        # Further clean the content using `lxml_html_clean`, we don't want trash!
        cleaner = Cleaner(page_structure=True, safe_attrs_only=True)
        cleaned_content: Any = cleaner.clean_html(content)

        # We save the data as a temporal file (not implemented here)
        if save_to_file:
            # Save content to a file
            file_name: str = title.replace(" ", "_") + ".html"
            with open(file_name, "w", encoding="utf-8") as file:
                file.write(cleaned_content)
            print(f"Reader mode content saved to '{file_name}'.")
        else:
            return cleaned_content

    # no internet?
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the content: {e}")


# Example usage
fetch_reader_mode_content("https://docs.python.org/3/library/functions.html")
