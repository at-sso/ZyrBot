import src.env as env


def main() -> int:
    __secrets = env.import_dot_folder(".secrets", "clownkey")
    env.f_wrapper(__secrets.init)
    return 0


if __name__ == "__main__":
    env.f_wrapper(main)
