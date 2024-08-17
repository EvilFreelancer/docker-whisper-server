import logging


def get_logger(level=logging.getLevelName(logging.INFO)) -> logging.Logger:
    logging.basicConfig(level=level)
    logger = logging.getLogger(__name__)
    logger.setLevel(level)
    return logger
