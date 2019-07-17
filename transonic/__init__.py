from ._version import __version__
from .justintime import jit, set_compile_jit

from .annotation import Array, NDim, Type, Shape, Union

from .aheadoftime import Transonic, boost, include

from .util import set_compile_at_import
from transonic.backends.pythranizer import wait_for_all_extensions

__all__ = [
    "__version__",
    "Transonic",
    "boost",
    "include",
    "Array",
    "NDim",
    "Type",
    "Shape",
    "Union",
    "jit",
    "set_compile_jit",
    "set_compile_at_import",
    "wait_for_all_extensions",
]
