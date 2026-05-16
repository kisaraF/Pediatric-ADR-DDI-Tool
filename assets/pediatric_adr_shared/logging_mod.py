import logging
import sys

def init_logger(module_name: str = __name__):
    """
    Instantiate a logging object for each module with DRY best practices
    """
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)
    # Avoid duplicated logs if the logger is created multiple times
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.propagate = False
    return logger