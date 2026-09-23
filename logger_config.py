import logging
import os
import sys


def setup_logger(log_dir: str = "Logs", log_file: str = "app.log") -> logging.Logger:
    """Настраивает логгер: пишет одновременно в консоль и в файл."""
    os.makedirs(log_dir, exist_ok=True)

    log_format = "%(asctime)s | [%(levelname)-7s] | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/file_txt.log", encoding="utf-8")

        ],
    )

    logger = logging.getLogger("PTPM-VKI")
    logger.info("Логгер успешно сконфигурирован")
    return logger