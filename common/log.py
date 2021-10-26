import logging

rootLogger = logging.getLogger('app')
rootLogger.setLevel(logging.INFO)
formatter = logging.Formatter(
        fmt="%(asctime)s - [%(filename)s:%(lineno)s - %(funcName)20s() ] - %(levelname)s - %(message)s"
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
inited = False
if not inited:
    rootLogger.addHandler(handler)
    inited = True

def setup_logger() -> logging.Logger:
    logger = logging.getLogger(f"app.{__name__}")
    logger.setLevel(logging.INFO)
    return logger
