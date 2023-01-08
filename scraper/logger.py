import logging

logger_name = "scraper"


def setup_logger():
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(levelname)s - %(asctime)s - %(name)s:%(filename)s - %(message)s"
    )
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(stream_handler)
    return logger


setup_logger()


def get_logger():
    return logging.getLogger(logger_name)
