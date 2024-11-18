import json
import google.generativeai as genai
from google.generativeai.types.generation_types import GenerateContentResponse

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

        self.__GEMINI_MODELS: NestedStringMap = {
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

        self.__models: Optional[StringMap] = self.__GEMINI_MODELS.get(model, None)
        """
        The specified `model` set by the user. 
        This retrieves the data directly from `__GEMINI_MODELS`.
        """
        if self.__models == None:
            raise FriendlyNameIsInvalid(f"Friendly name: '{model}' is invalid.")

        # If `secrets` was initialized and models is not `None`, start the API.
        genai.configure(api_key=secrets.get())
        self.gemini_model = genai.GenerativeModel(
            model_name=self.__models["MODELNAME"],
        )

    def get_dict_response(self, request: str) -> str:
        data: GenerateContentResponse = self.gemini_model.generate_content(request)
        return json.dumps(data.to_dict())
