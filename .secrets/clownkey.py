import os
import subprocess
from getpass import getpass

from src.env import *
from src.env.globales import *
from src.env.locales import flags, EnvStates

from src.function_wrapper import f_wrapper


class __DecryptionError(Exception):
    def __init__(self, s: object) -> None:
        super().__init__(s)


class __KeyManagerNotInitialized(Exception):
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
        exc=FileNotFoundError,
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
            f"Flag 'deadInternet' detected. API key retrieval is impossible. Function '{friendly.full_name(get)}' will terminate the program."
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

    logger.info(f"Checking encryption type of '{ENCRYPTED_KEY_FILE}'.")
    # Verify encryption type and validity of the encrypted file
    secret_type: str = __get_encryption_type(ENCRYPTED_KEY_FILE)
    if secret_type == EnvStates.environment_error.value:
        logger.critical("Failed to retrieve encryption type.", exc=__DecryptionError)
    else:
        logger.debug(f"Secret info of '{ENCRYPTED_KEY_FILE}': [\n{secret_type}].")

    __init_was_called = True
    logger.debug(
        f"{friendly.full_name(get)}: {f_wrapper.init(get, decrypt=False).status}"
    )


def __get_encryption_type(f: str) -> str:
    """
    Determines the encryption type of a file by calling GPG.
    Returns the encryption details as a string, or None if unsuccessful.
    """
    try:
        # Run the `gpg --list-packets` command and capture the output
        result = subprocess.run(
            ["gpg", "--list-packets", f],
            capture_output=True,
            text=True,  # Ensures the output is a string, not bytes
            check=True,  # Raises an error if the command fails
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.critical(e)
        return EnvStates.environment_error.value


def get(decrypt: bool) -> str:
    """
    Decrypts the encrypted API key using GPG with the provided password.

    Important:
    - Do not store or print the decrypted API key in plain text. This could pose a significant security risk.
    - Use the decrypted key immediately and securely. Avoid storing it in variables or logging it.

    @parm decrypt (bool): Whether to decrypt the API key.

    @return The decrypted API key if `decrypt` is True, otherwise a success indicator.
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
        return decrypted_data.decode().strip()
    return EnvStates.success.value
