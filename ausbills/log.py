import logging


def get_logger(name: str, level=logging.WARNING) -> logging.Logger:
    logging.basicConfig(level=level)
    return logging.Logger(name=name)
