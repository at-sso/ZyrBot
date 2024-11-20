import json
import google.generativeai as genai
from icecream import ic

from .exc import *
from ..env import *


def _modelname_desc(model: LitStr, desc: LitStr) -> StringMap:
    """Creates a dictionary mapping a model name to its description."""
    return {"MODELNAME": model, "DESCRIPTION": desc}


class GeminiModel:
    """
    This class provides a virtual interface to interact with a Gemini model, allowing you to
    send prompts and receive responses.
    """

    def __init__(self, model: str) -> None:
        # If `secrets` was not initialized, raise exception.
        if not secrets.was_initialized():
            raise ImpossibleKeyRetrieval(
                f"Module '{secrets.__name__}' was not correctly initialized."
            )

        self.__LISTED_MODELS: NestedStringMap = {
            "1.5-flash": _modelname_desc(
                model="gemini-1.5-flash",
                desc="A versatile model excelling in various tasks.",
            ),
            "1.5-flash-8b": _modelname_desc(
                model="gemini-1.5-flash-8b",
                desc="Optimized for high-volume, less complex tasks.",
            ),
            "1.5-pro": _modelname_desc(
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

        self.__selected_model: Optional[StringMap] = self.__LISTED_MODELS.get(
            model, None
        )
        """
        The specified `model` set by the user. 
        This retrieves the data directly from `__GEMINI_MODELS`.
        """
        if self.__selected_model == None:
            raise FriendlyNameIsInvalid(f"Friendly name: '{model}' is invalid.")

        self.model_name: str = self.__selected_model["MODELNAME"]
        self.description: str = self.__selected_model["DESCRIPTION"]

        # If `secrets` was initialized and models is not `None`, start the API.
        genai.configure(api_key=secrets.get())
        self.gemini = genai.GenerativeModel(
            model_name=self.__selected_model["MODELNAME"],
        )
        logger.debug(
            f"Gemini model selected: {self.model_name}. API should be working now."
        )

    def get_response(self, request: MediaList) -> GenericKeyMap:
        """
        this function does not handle the image, handling the image must be managed outside this scope.
        format:
            only string request: `["..."]`
            analyze image request: `["...", ImageFile]`
            any: raise `InvalidAIRequestFormat`
        if somehow request is impossible to analyze, and `data` is `None`, raise `AIRequestFailure`
        """
        logger.debug(f"Function {friendly.func_info(self.get_response)} was called.")

        data: NullableContentResponse = None

        # Handle the request format:
        if self.__is_single_str(request):
            logger.info("The `request` object only contains a string.")
            # The first (0) index of `request` is always a string.
            data = self.__handle_response(request[0])

        elif self.__is_str_and_image(request):
            logger.info("The `request` object contains an image to analyze.")
            # The second (1) index of `request` is always an `ImageFile` object.
            data = self.__handle_response(request)

        else:
            raise InvalidAIRequestFormat("The format of `request` is invalid.")

        # Check the if the `data` is valid.
        ic(data)
        if data is None:
            raise AIRequestFailure(
                "Failed to retrieve data from the Gemini API. "
                f"The requested object '{friendly.full_name(data)}' is `None`.\n"
                "Check the logger for more information."
            )

        return json.loads(json.dumps(data.to_dict()))

    def __is_single_str(self, req: MediaList, index: int = 1) -> bool:
        """
        Checks if the request contains only a single string.
        The `index` argument is a helper for the `__is_str_and_image` method.
        """
        if index <= 0 or index >= 3:
            raise IndexError()
        return len(req) == index and isinstance(req[0], str)

    def __is_str_and_image(self, req: MediaList) -> bool:
        """Checks if the request contains a string followed by an ImageFile."""
                # Handle edge case where the first element of `request` is an empty string.
        if req[0] == "":
            req[0] = "Can you please analyze this image for me?"
        return self.__is_single_str(req, 2) and isinstance(req[1], ImageFile)

    def __handle_response(self, res: MediaElement) -> NullableContentResponse:
        a: NullableContentResponse = None
        try:
            # If ANY error occurs this will raise an exception.
            a = self.gemini.generate_content(res)
        except Exception as e:
            logger.error(e)
            return None
        return a
