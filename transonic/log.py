"""Logging
==========

Defines the transonic logger (variable :code:`logger`).

"""

import logging
from types import MethodType
import os

def create_logger(name, show_time=False, show_path=False):
    """Returns a logger instance using ``rich`` package if available; else
    defaults to ``logging`` standard library.

    """
    try:
        from rich.logging import RichHandler

        handler = RichHandler(show_time=show_time, show_path=show_path)
    except ImportError:
        handler = logging.StreamHandler()

    logger = logging.getLogger(name)
    logger.addHandler(handler)
    return logger


def get_logger(name):
    """Returns a logger instance using ``rich`` package if available; else
    defaults to ``logging`` standard library.

    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger = create_logger(name)
    return logger


logger = create_logger("transonic")


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
