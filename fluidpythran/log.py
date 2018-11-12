"""logging
==========

"""

import logging

logger = logging.getLogger("fluidpythran")

# Initialize logging
try:
    # Set a nice colored output
    from colorlog import ColoredFormatter

    formatter = ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red",
        },
    )
    stream = logging.StreamHandler()
    stream.setFormatter(formatter)
    logger.addHandler(stream)
except ImportError:
    # No color available, use default config
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logger.info("Disabling color, you really want to install colorlog.")


def set_log_level(level):
    """Set logging level"""
    level = level.lower()
    if level == "info":
        level = logging.INFO
    elif level == "debug":
        level = logging.DEBUG

    logger.setLevel(level)


set_log_level("info")
