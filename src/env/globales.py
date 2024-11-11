import os

from .ptypes import *
from .locales import flags, EnvInfo

######################################################################################################
# Absolute paths for commonly used directories.
# Execution paths:
CURRENT_PATH: str = EnvInfo.current_path
"""Absolute path to the execution folder.
NOTE: Running this path from another directory (other than main.py) may cause unexpected behavior."""
SOURCE_FOLDER: str = f"{CURRENT_PATH}/src"
"Source code path."
SECRETS_FOLDER: str = f"{CURRENT_PATH}/.secrets"
######################################################################################################


######################################################################################################
# Logger paths:
LOGGER_FOLDER_PATH: str = f"{CURRENT_PATH}/.log"
LOGGER_FILE: str = os.path.join(LOGGER_FOLDER_PATH, flags.loggerName)
LOGGER_MAX_BACKUP: int = flags.loggerMaxBackup
######################################################################################################
