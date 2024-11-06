import os
import subprocess
from getpass import getpass

from src.env import *
from src.env.globales import *
from src.env.locales import flags, EnvStates


class __DecryptionError(Exception):
    def __init__(self, message: object) -> None:
        super().__init__(message)


# Constants for default values and file paths
PASSWORD_FILE_PATH: str = f"{SECRETS_FOLDER}/password.txt"
ENCRYPTED_KEY_FILE: str = f"{SECRETS_FOLDER}/key.gpg"

__f_exists: Callable[[str], bool] = lambda f: os.path.isfile(f)
__secrets: bytes = bytes()  # Not set (yet)
__is_extraSecrets_set: bool = flags.extraSecret != EnvStates.environment_error

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
    logger.info(
        "GPG might ask for your passphrase from time to time. This is normal behavior!"
    )

    # Check if `noWinget` flag is set and log warnings
    if not flags.noWinget:
        logger.warning("Flag `noWinget` is being used.")

    # If the system is Windows, always try to install or update Gpg4win.
    if EnvInfo.system == "Windows" and flags.noWinget:
        logger.info("Trying to install 'Gpg4win'.")
        subprocess.run(["winget", "install", "--id", "GnuPG.Gpg4win"])

    # Handle password loading or prompting
    if not __f_exists(PASSWORD_FILE_PATH) and __is_extraSecrets_set:
        api_password: str = EnvStates.environment_error
        logger.warning("Password file doesn't exist!")
        api_password = getpass("API key password: ")

        # Only save the password to the file if `doNotSaveMyKey` is set
        if flags.doNotSaveMyKey:
            # Write the password into the file
            with open(PASSWORD_FILE_PATH, "w") as f:
                f.write(api_password)
        flags.extraSecret = api_password
        logger.info("Password was set manually.")
    else:
        logger.info(
            "API password file exists or 'extraSecret' is set. "
            "Assuming the password is correct..."
        )
        if not __is_extraSecrets_set:
            with open(PASSWORD_FILE_PATH, "rb") as f:
                flags.extraSecret = f.read()

    logger.info(f"Checking encryption type of '{ENCRYPTED_KEY_FILE}'.")
    # Verify encryption type and validity of the encrypted file
    secret_type: str = __get_encryption_type(ENCRYPTED_KEY_FILE)
    if secret_type == EnvStates.unknown_type:
        logger.critical("Failed to retrieve encryption type.", __DecryptionError)
    else:
        logger.debug(f"Secret info of '{ENCRYPTED_KEY_FILE}': [\n{secret_type}].")


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
        return EnvStates.unknown_type


def get_secrets() -> str:
    """
    Decrypts the encrypted API key using GPG with the provided password.
    Is a good idea to not store the value of this function in a variable.
    """
    process = subprocess.Popen(
        ["gpg", "--decrypt", "--batch", "--passphrase", flags.extraSecret],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    decrypted_data, error = process.communicate(input=__secrets)

    if process.returncode != 0:
        raise __DecryptionError(f"Decryption failed: {error.decode().strip()}")

    return decrypted_data.decode().strip()
