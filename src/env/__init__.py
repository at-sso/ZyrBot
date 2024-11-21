import sys as _sys
import importlib.util as _import_util
from importlib.machinery import ModuleSpec as _ModuleSpec
from pathlib import Path as _Path
from types import ModuleType as _ModuleType

from .ptypes import *
from .friendly_generics import friendly
from .globales import *
from .logger import logger
from .locales import flags, EnvInfo, EnvStates


class BaseException(Exception):
    def __init__(self, s: object, name: Optional[object] = None) -> None:
        logger.critical(
            f"{name if name != None else EnvStates.unknown_location.value}: {s}"
        )
        super().__init__(s)


def import_dot_folder(folder_name: LitStr, module_name: LitStr) -> _ModuleType:
    # Locate the .dot folder path
    dot_folder_path: _Path = _Path(folder_name).resolve()
    module_file: _Path = dot_folder_path / f"{module_name}.py"

    if not module_file.is_file():
        raise ModuleNotFoundError(f"No module named '{module_name}' in {folder_name}")

    # Load the module dynamically
    spec: Optional[_ModuleSpec] = _import_util.spec_from_file_location(
        module_name, module_file
    )
    module: _ModuleType = _import_util.module_from_spec(spec)  # type: ignore[reportArgumentType]
    _sys.modules[module_name] = module
    spec.loader.exec_module(module)  # type: ignore[reportOptionalMemberAccess]

    return module


secrets = import_dot_folder(".secrets", "clownkey")
"""Secrets!"""
