from src.ui import Interface, ft
from src.function_wrapper import f_wrapper
from src.env import *
from src.env.ptypes import *


def main() -> str:
    try:
        # Start the key manager handling.
        f_wrapper.init(secrets.init)
        f_wrapper.init(secrets.get)
        # Start Flet engine and UI.
        f_wrapper.init(
            f=ft.app,  # type: ignore[reportUnknownArgumentType]
            target=Interface,
            name=EnvInfo.program_name.value,
            assets_dir="assets",
        )
    finally:
        results: str = f_wrapper.func_results
        logger.debug(
            f"Results: {results if results != '{}' else EnvStates.unknown_value}"
        )

    return EnvStates.success.value


if __name__ == "__main__":
    end_status = f_wrapper.handler(main).status
    main_name = friendly.func_info(main)
    if end_status == EnvStates.environment_error.value:
        logger.error(f"An unknown error occurred while handling '{main_name}'.")
    logger.debug(f"{main_name}, returned: {end_status}")
