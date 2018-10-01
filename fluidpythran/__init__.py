
import inspect

from ._version import __version__

__all__ = [
    "__version__",
    "monkey_patch_function",
    "is_pythranized",
    "use_pythranized_block",
]


def monkey_patch_function(func):
    return func


def is_pythranized():
    return False


def use_pythranized_block(name):

    frame = inspect.currentframe()
    try:
        locals_caller = frame.f_back.f_locals
    finally:
        del frame

    raise NotImplementedError
