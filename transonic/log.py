"""Logging
==========

Defines the transonic logger (variable :code:`logger`).

"""

import logging
from types import MethodType
import os

logger = logging.getLogger("transonic")

# Initialize logging
try:
    from rich.logging import RichHandler

    logger.addHandler(RichHandler())
except ImportError:
    # No color available, use default config
    logging.basicConfig(format="%(levelname)s: %(message)s")
    logger.info("Disabling color, you really want to install rich.")


def _get_level_number(level):
    level = level.lower()
    if level == "info":
        return logging.INFO
    elif level == "debug":
        return logging.DEBUG
    elif level == "warning":
        return logging.WARNING
    else:
        raise ValueError


def set_level(self, level):
    """Set logging level"""
    if not level:
        self.setLevel(0)
        return

    level = _get_level_number(level)

    self.setLevel(level)


def get_level(self):
    return logging.getLevelName(self.getEffectiveLevel()).lower()


def is_enable_for(self, level):
    return _get_level_number(level) >= self.getEffectiveLevel()


logger.set_level = MethodType(set_level, logger)
logger.get_level = MethodType(get_level, logger)
logger.is_enable_for = MethodType(is_enable_for, logger)

if os.getenv("TRANSONIC_DEBUG"):
    level = "debug"
else:
    level = "info"

logger.set_level(level)
