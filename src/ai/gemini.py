import json
from pathlib import Path
import google.generativeai as genai
from icecream import ic

from .tools.exc import *
from src.env import *


def _modelname_desc(model: LitStr, desc: LitStr) -> StringMap:
    """Creates a dictionary mapping a model name to its description."""
    return {"MODELNAME": model, "DESCRIPTION": desc}


GEMINI_MODEL_NAMES: StringList = ["1.5-flash", "1.5-flash-8b", "1.5-pro"]
"""List of model names."""


class GeminiModel:
    """
    This class provides a virtual interface to interact with a Gemini model, allowing you to
    send prompts and receive responses.
    """

    def __init__(self, model: Optional[str] = None, do_raise: bool = True) -> None:
        # If `model` is invalid, raise an exception if needed.
        if model is None or model not in GEMINI_MODEL_NAMES:
            m: str = (
                f"The model of {self.__class__} is invalid or 'NoneType'. This class will not initialize."
            )
            if do_raise:
                raise AIModelIsInvalid(m)
            logger.warning(m)
            return

        # If `secrets` was not initialized, raise exception.
        if not secrets.was_initialized():
            raise ImpossibleKeyRetrieval(
                f"Module '{secrets.__name__}' was not correctly initialized."
            )

        self.__LISTED_MODELS: NestedStringMap = {
            GEMINI_MODEL_NAMES[0]: _modelname_desc(
                model="gemini-1.5-flash",
                desc="A versatile model excelling in various tasks.",
            ),
            GEMINI_MODEL_NAMES[1]: _modelname_desc(
                model="gemini-1.5-flash-8b",
                desc="Optimized for high-volume, less complex tasks.",
            ),
            GEMINI_MODEL_NAMES[2]: _modelname_desc(
                model="gemini-1.5-pro",
                desc="A powerful model for intricate reasoning and complex tasks.",
            ),
        }
        """
        A nested dictionary mapping friendly model names to detailed information. 

        Each entry contains:
        - "MODELNAME": The technical name of the model.
        - "DESCRIPTION": A brief description of the model's capabilities.
        """

        self.selected_model: Optional[StringMap] = self.__LISTED_MODELS.get(model, None)
        """
        The specified `model` set by the user. 
        This retrieves the data directly from `__GEMINI_MODELS`.
        """
        if self.selected_model == None:
            raise FriendlyNameIsInvalid(f"Friendly name: '{model}' is invalid.")
        self.model_name: str = self.selected_model["MODELNAME"]
        self.description: str = self.selected_model["DESCRIPTION"]

        # If `secrets` was initialized and models is not `None`, start the API.
        genai.configure(api_key=secrets.get(decrypt=True)["GEMINI"])
        self.__gemini = genai.GenerativeModel(
            model_name=self.selected_model["MODELNAME"],
        )
        self.__gemini_history: MemoryList = []

        logger.debug(
            f"Gemini model selected: {self.model_name}. API should be working now."
        )

    def get_response(self, request: MediaList) -> Path:
        """
        this function does not handle the image, handling the image must be managed outside this scope.
        format:
            only string request: `["..."]`
            analyze image request: `["...", ImageFile]`
            any: raise `InvalidAIRequestFormat`
        if somehow request has an error `data` will be `None`, and this will raise `AIRequestFailure`
        """
        friendly.i_was_called(self.get_response)

        data: NullableContentResponse = None

        # Handle the request format:
        if self.__req_is_str(request):
            logger.info("Request only has a string.")
            # The first (0) index of `request` is always a string.
            self.__add_history("user", request[0])
            data = self.__handle_response()

        elif self.__req_is_str_n_image(request):
            logger.info("The `request` object contains an image to analyze.")
            # The second (1) index of `request` is always an `ImageFile` object.
            self.__add_history("user", request)
            data = self.__handle_response()

        else:
            raise InvalidAIRequestFormat("The format of `request` is invalid.")

        # Check the if the `data` is valid.
        ic(data)
        if data is None:
            raise AIRequestFailure(
                "Failed to retrieve data from the Gemini API. "
                f"The requested object '{friendly.var_info(data)}' is `None`.\n"
                "Check the logger for more information."
            )

        # Write the JSON response into a file in the local cache location.
        latest_res: Path = Path(globales.CACHE_FOLDER) / "latest_response.json"
        json_res: str = json.dumps(data.to_dict(), indent=1)
        latest_res.write_text(json_res)

        return latest_res

    def get_final_response(self, data: GenericKeyMap) -> str:
        return data["candidates"][0]["content"]["parts"][0]["text"]

    def __add_history(self, role: str, content: object) -> GenericKeyMap:
        """Adds a message to the chat history."""
        friendly.i_was_called(self.__add_history)
        history_entry: GenericKeyMap = {"role": role, "parts": content}
        self.__gemini_history.append(history_entry)
        return history_entry

    def __req_is_str(self, request: MediaList, index: int = 1) -> bool:
        """
        Checks if the request contains only a single string.
        The `index` argument is a helper for the `__is_str_and_image` method.
        """
        friendly.i_was_called(self.__req_is_str)
        if not request[0]:
            raise RuntimeError(
                "An empty string was received but expected a non-empty value."
            )
        if index <= 0 or index >= 3:
            raise IndexError(
                f"The `index` argument at {friendly.func_info(self.__req_is_str)} is invalid."
            )
        return len(request) == index and isinstance(request[0], str)

    def __req_is_str_n_image(self, request: MediaList) -> bool:
        """Checks if the request contains a string followed by an ImageFile."""
        # Handle edge case where the first element of `request` is an empty string.
        if not request[0]:
            request[0] = "Can you please analyze this image for me?"
        return self.__req_is_str(request, 2) and isinstance(request[1], ImageFile)

    def __handle_response(self) -> NullableContentResponse:
        friendly.i_was_called(self.__handle_response)
        logger.debug(self.__gemini_history)

        try:
            response = self.__gemini.generate_content(self.__gemini_history)
            self.__add_history("gemini", response.candidates[0].content)
        except Exception as e:
            logger.error(e)
            return None

        return response
