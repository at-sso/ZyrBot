import src.env as env
from src.env import logger

logger.in_shell = True


def main() -> int:
    __secrets = env.import_dot_folder(".secrets", "clownkey")
    __secrets.test()
    return 0


if __name__ == "__main__":
    env.f_wrapper(main)
