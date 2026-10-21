from logger_config import setup_logger
from triangle import process_triangle


def main() -> None:
    logger = setup_logger()
    logger.info("Приложение запущено")

    while True:
        print("\n--- Новый треугольник (Enter без ввода — выход) ---")

        raw_a = input("Сторона A: ").strip()
        # выход, если пользователь ничего не ввёл
        if raw_a == "":
            logger.info("Пользователь завершил работу (пустой ввод)")
            break

        raw_b = input("Сторона B: ").strip()
        raw_c = input("Сторона C: ").strip()

        # можно также разрешить команды выхода на любом шаге
        if raw_b.lower() in ("exit", "quit") or raw_c.lower() in ("exit", "quit"):
            logger.info("Пользователь завершил работу (команда выхода)")
            break

        kind, coords = process_triangle(raw_a, raw_b, raw_c)

        print(f"Вид: {kind}")
        print(f"Координаты: {coords}")

    logger.info("Приложение завершило работу")


if __name__ == "__main__":
    main()