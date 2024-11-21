import json
from enum import Enum

from .logger import logger
from .locales import EnvStates
from .ptypes import *


def _custom_serializer(obj: Any) -> Any | str:
    # Handle enums and other non-serializable objects
    if isinstance(obj, Enum):
        return obj.value
    elif hasattr(obj, "__dict__"):
        return __FriendlyGenerics.full_name(obj)
    return str(obj)  # Default to string representation


class __FriendlyGenerics:
    @staticmethod
    def var_type(v: object) -> str:
        """
        Determines the type of a variable.

        @param x: The variable whose type is to be determined.
        @return: The name of the type as a string.
        """
        return f"({type(v).__name__})"

    @staticmethod
    def unique_id(v: object) -> str:
        """
        Generates a unique identifier string for a given variable.

        @param x: The variable to generate the identifier for.
        @return: A string representing the unique memory address of the variable.
        """
        return f"id: {id(v)}"

    @staticmethod
    def full_name(x: object, err: str = EnvStates.unknown_location.value) -> str:
        """
        Gets the fully qualified name of a callable or variable.

        @param x: The callable or variable.
        @param err (optional): Error name.
        @return: The fully qualified name or `err` if the qualified name is unknown.
        """
        try:
            return f"{x.__module__}.{x.__qualname__}"
        except AttributeError:
            return err

    def var_info(self, v: object) -> str:
        """
        Provides detailed information about a variable including its type, class, and unique identifier.

        @param f: The variable to analyze.
        @return: A string with the full name, type, and unique identifier of the variable.
        """
        return f"{self.full_name(v)}, {self.var_type(v)}, {self.unique_id(v)}"

    def func_info(self, f: GenericCallable) -> str:
        """
        Provides detailed information about a callable including its class and unique identifier.

        @param f: The callable to analyze.
        @return: A string with the full name and unique identifier of the callable.
        """
        return f"{self.full_name(f, f.__name__)}, {self.unique_id(f)}"

    @staticmethod
    def map_keys(d: GenericMap) -> str:
        """
        Returns a string representation of all keys in a dictionary.

        @param d: The dictionary to retrieve keys from.
        @return: A string list of all keys.
        """
        return f"{list(d.keys())}"

    @staticmethod
    def map_items(d: GenericMap) -> str:
        """
        Returns a string representation of all key-value pairs in a dictionary.

        @param d: The dictionary to retrieve items from.
        @return: A string list of all key-value pairs.
        """
        return f"{list(d.items())}"

    @staticmethod
    def get_map_key_item(d: GenericMap, key: object) -> str:
        """
        Retrieves the value associated with a key in a dictionary and formats it as a string.

        Returns "BADVALUE" if the key is not found.

        @param d: The dictionary to search.
        @param key: The key to look for.
        @return: A formatted string of the key-value pair or "BADVALUE".
        """
        err = EnvStates.unknown_value.value
        item = d.get(key, err)
        if item == err:
            return err
        return f"<{key}: {item}>"

    def get_key_from_item(self, d: GenericMap, item: object) -> str:
        """
        Searches for a given item in a dictionary and retrieves its key.

        This method can be slow because it involves reversing the dictionary search.
        Returns "BADVALUE" if the item is not found.

        @param d: The dictionary to search.
        @param item: The item to search for.
        @return: The key associated with the item or "BADVALUE".
        """
        # Create a reversed dictionary to map items back to keys
        reversed_dict = {value: key for key, value in d.items()}
        return self.get_map_key_item(reversed_dict, item)

    def iter_info(self, it: Iterable[object]) -> str:
        """Show the iterator type and the contents. The contents are formatted to be readable and friendly."""
        content = [self.var_info(item) for item in it]
        return f"Iterable {self.var_type(it)} = {content}"

    def jsonify_values(
        self,
        content: GenericKeyMap,
        given_var: object,
        err: object,
        *args: object,
    ) -> str:
        """
        Populates the `content` dictionary with the status of each variable or callable in `args`.

        This function iterates over an iterable of variables or callables (`args`) and assigns each
        a corresponding status in the `content` dictionary based on its value:
            - If the variable is `None`, it is assigned `EnvStates.success`.
            - If the variable matches the provided `err` value, it is assigned `EnvStates.unknown_value`.
            - Otherwise, the variable's own value is stored as its status.

        @param content (GenericKeyMap): A dictionary to store the statuses of variables or callables.
        @param err (object): A value representing an error state. If a variable in `args` matches this value, it is assigned `EnvStates.unknown_value`.
        @param *args (object): An iterable of variables or callable functions whose statuses will be stored in `content`.

        Returns:
            str: A JSON-formatted string representing the `content` dictionary, with the statuses of each variable.
        """
        for var in args:
            name: str = self.var_info(var)
            if given_var is None:
                # If the function returned None, assign EnvStates.success as default
                content[name] = EnvStates.success.value
            elif given_var == err:
                # Explicitly set to unknown value if an error occurs
                content[name] = EnvStates.unknown_value.value
            else:
                # For all other cases, store the status as is
                content[name] = given_var

        # Get the formatted results in JSON.
        return json.dumps(content, indent=4, default=_custom_serializer)

    def jsonify_generic_values(self, *args: object) -> str:
        """Does the same as `jsonify_values`, but uses local variables instead."""
        _: GenericKeyMap = {}
        for var in args:
            name: str = f"{self.var_type(var)}, {self.unique_id(var)}"
            _[name] = str(var)
        return json.dumps(_, indent=4, default=_custom_serializer)

    def i_was_called(self, f: GenericCallable, log: bool = False) -> str:
        """
        Returns a string representation of a callable being called.

        @param f: The callable to analyze.
        @param log: Allows this function to log at level 'INFO' the returned message.
        @return: A string with the full name and unique identifier of the callable being called.
        """
        _: str = f"Callable '{self.full_name(f, f.__name__)}' was called."
        if log:
            logger.info(_)
        return _


friendly = __FriendlyGenerics()
"""Provide user-friendly string representations for generic values."""
