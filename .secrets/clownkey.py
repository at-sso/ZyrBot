import json
import os
import subprocess
from getpass import getpass

from src.env import *
from src.env.globales import *
from src.env.locales import flags, EnvStates

from src.helpers import *


class __DecryptionError(BaseException):
    def __init__(self, s: object) -> None:
        super().__init__(s)


class __KeyManagerNotInitialized(BaseException):
    def __init__(self, s: object) -> None:
        super().__init__(s)


# Constants for default values and file paths
PASSWORD_FILE_PATH: str = f"{SECRETS_FOLDER}/password.txt"
ENCRYPTED_KEY_FILE: str = f"{SECRETS_FOLDER}/key.gpg"

__f_exists: Callable[[str], bool] = lambda f: os.path.isfile(f)
"""Check if a file exists."""
__secrets: bytes = bytes()  # Not set (yet)
"""Binary of secret file (key.gpg)"""
__init_was_called: bool = False


if not __f_exists(ENCRYPTED_KEY_FILE):
    logger.critical(
        f"An encrypted API key was not found in: '{SECRETS_FOLDER}'!\n"
        "You can only (and must) use encrypted files in this environment. "
        "Please check the documentation for more information.",
        exc=FileNotFoundError if not flags.deadInternet else Exception,
    )
else:
    with open(ENCRYPTED_KEY_FILE, "rb") as f:
        __secrets = f.read()


def init() -> None:
    """
    Initializes the environment by setting up passwords, checking for dependencies,
    and ensuring encryption requirements are met.
    """
    if flags.deadInternet:
        logger.warning(
            "Flag 'deadInternet' detected. API key retrieval is impossible. "
            f"Function '{friendly.full_name(get)}' will terminate the program."
        )
        return

    global __init_was_called
    logger.info(
        "GPG might ask for your passphrase from time to time. This is normal behavior!"
    )

    # If the system is Windows, always try to install or update Gpg4win.
    if EnvInfo.system.value == "Windows" and flags.noWinget:
        logger.info("Trying to install 'Gpg4win'.")
        subprocess.run(["winget", "install", "--id", "GnuPG.Gpg4win"])

    # Handle password loading or prompting
    if not (__f_exists(PASSWORD_FILE_PATH) and flags.help.is_extraSecrets_set):
        api_password: str | bytes = EnvStates.unknown_value.value
        logger.warning("Password file doesn't exist!")
        # This makes debugging a little more "save"; since the data is not being shown directly.
        api_password = getpass("API key password: ").encode("utf-32")

        # Only save the password to the file if `doNotSaveMyKey` is set
        if flags.doNotSaveMyKey:
            # Write the password into the file
            with open(PASSWORD_FILE_PATH, "w") as f:
                logger.debug("Flag 'doNotSaveMyKey' is disabled!")
                f.write(api_password.decode("utf-32"))

        flags.extraSecret = api_password
        logger.info("Password was set manually.")
    else:
        a = str
        if flags.help.is_extraSecrets_set:
            a = "API password file exists."
            with open(PASSWORD_FILE_PATH, "r") as f:
                flags.extraSecret = f.read().encode("utf-32")
        else:
            a = "Flag 'extraSecret' was set."
        logger.info(a + " Assuming the password or secret is correct...")

    __init_was_called = True
    logger.debug(
        f"{friendly.full_name(get)}: {f_wrapper.init(get, decrypt=False).status}"
    )


def get(decrypt: bool = False) -> GenericKeyMap | str:
    """
    Decrypts the encrypted API key using GPG with the provided password.

    Important:
    - Do not store or print the decrypted API key in plain text. This could pose a significant security risk.
    - Use the decrypted key immediately and securely. Avoid storing it in variables or logging it.

    Extremely important (Dev notes):
    - If `decrypt` is True, the returned value WILL BE A DICTIONARY! Keep this in mind while handling the result.
    - The keys hold the API key of its given name, for example: "GEMINI", returns the API key of Google AI Gemini.
    - The following keys are expected to be returned:

    >>> ["GEMINI", "GCLOUD"]

    @parm decrypt (bool): Whether to decrypt the API key.
    @return The decrypted API keys if `decrypt` is True, otherwise a success indicator.
    """
    if not __init_was_called:
        raise __KeyManagerNotInitialized(
            f"Operation: {friendly.full_name(init)} was not initialized."
        )

    process = subprocess.Popen(
        [
            "gpg",
            "--decrypt",
            "--batch",
            "--passphrase",
            flags.extraSecret.decode("utf-32"),
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    decrypted_data, error = process.communicate(input=__secrets)

    if process.returncode != 0:
        raise __DecryptionError(f"Decryption failed: {error.decode().strip()}")

    logger.info("Decryption success.")
    if decrypt:
        return json.loads(decrypted_data.decode().strip())
    return EnvStates.success.value


def was_initialized() -> bool:
    logger.debug(f"{friendly.full_name(was_initialized)}: {__init_was_called}")
    return __init_was_called
