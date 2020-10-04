import logging

logging.basicConfig(level=logging.INFO)


def get_logger(name: str) -> logging.Logger:
    return logging.Logger(name=name)
