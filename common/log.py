import logging


def setup_logger() -> logging.Logger:
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(module)s - %(message)s"
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger
