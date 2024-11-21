import json
import google.generativeai as genai
from icecream import ic

from .exc import *
from ..env import *
import PIL.Image


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
        self.__gemini = genai.GenerativeModel(
            model_name=self.__selected_model["MODELNAME"],
        )
        self.__gemini_history = []

        logger.debug(
            f"Gemini model selected: {self.model_name}. API should be working now."
        )

    def get_response(self, request: MediaList) -> tuple[GenericKeyMap, EnvStates]:
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
        state: EnvStates

        # Handle the request format:
        if self.__is_single_str(request):
            logger.info("The `request` object only contains a string.")
            # The first (0) index of `request` is always a string.
            data, state = self.__handle_response(request[0])

        elif self.__is_str_and_image(request):
            raise NotImplementedError()
            logger.info("The `request` object contains an image to analyze.")
            # The second (1) index of `request` is always an `ImageFile` object.
            data, state = self.__handle_response(request)

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

        return json.loads(json.dumps(data.to_dict())), state

    def __is_single_str(self, req: MediaList, index: int = 1) -> bool:
        """
        Checks if the request contains only a single string.
        The `index` argument is a helper for the `__is_str_and_image` method.
        """
        friendly.i_was_called(self.__is_single_str)

        if index <= 0 or index >= 3:
            raise IndexError(
                f"The `index` argument at {friendly.func_info(self.__is_single_str)} is invalid."
            )
        return len(req) == index and isinstance(req[0], str)

    def __is_str_and_image(self, req: MediaList) -> bool:
        """Checks if the request contains a string followed by an ImageFile."""
        # Handle edge case where the first element of `request` is an empty string.
        friendly.i_was_called(self.__is_str_and_image)

        if req[0] == "":
            req[0] = "Can you please analyze this image for me?"
        return self.__is_single_str(req, 2) and isinstance(req[1], ImageFile)

    def __handle_response(
        self,
        res: MediaElement,
    ) -> tuple[NullableContentResponse, EnvStates]:
        """Handle the responses of the API. If any error occurs set `data` to `None`."""
        friendly.i_was_called(self.__handle_response)

        # Returned data from the AI
        data: NullableContentResponse = None

        try:
            # If ANY error occurs this will raise an exception.
            data = self.__gemini.generate_content(...)
        except Exception as e:
            logger.error(e)
            data = None
            return data, EnvStates.function_error

        return data, EnvStates.success
