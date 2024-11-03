import src.env as env
from src.env import logger
from src.env import *

logger.in_shell = True


def main() -> int:
    __secrets = env.import_dot_folder(".secrets", "clownkey")
    __secrets.init()
    return 0


if __name__ == "__main__":
    env.f_wrapper(main)
