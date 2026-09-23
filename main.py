from logger_config import setup_logger
from triangle import process_triangle


def main() -> None:
    logger = setup_logger()
    logger.info("Приложение запущено")

    raw_a = input("Сторона A: ")
    raw_b = input("Сторона B: ")
    raw_c = input("Сторона C: ")

    kind, coords = process_triangle(raw_a, raw_b, raw_c)

    print(kind)
    print(coords)

    logger.info("Приложение завершило работу")


if __name__ == "__main__":
    main()