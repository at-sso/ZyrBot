__all__ = [
    "CURRENT_PATH",
    "SOURCE_FOLDER",
    "LOGGER_FOLDER_PATH",
    "LOGGER_FILE",
]

import os
import sys
from datetime import datetime

######################################################################################################
# Absolute paths for commonly used directories.
# Execution paths:
CURRENT_PATH: str = os.path.abspath(os.path.dirname(sys.argv[0])).replace("\\", "/")
"""Absolute path to the execution folder.
NOTE: Running this path from another directory (other than main.py) may cause unexpected behavior."""
SOURCE_FOLDER: str = f"{CURRENT_PATH}/src"
"Source code path."
######################################################################################################


######################################################################################################
# Logger paths:
LOGGER_FOLDER_PATH: str = f"{CURRENT_PATH}/.log"
LOGGER_FILE: str = os.path.join(
    LOGGER_FOLDER_PATH,
    (f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}") + ".log",
)
######################################################################################################
