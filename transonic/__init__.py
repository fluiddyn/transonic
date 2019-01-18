from ._version import __version__
from .justintime import jit, set_compile_jit

try:
    from ._path_data_tests import path_data_tests
except ImportError:
    pass

from .annotation import Array, NDim, Type, Shape, Union

from .aheadoftime import Transonic, boost, make_signature, include

from .util import set_compile_at_import
from .pythranizer import wait_for_all_extensions

__all__ = [
    "__version__",
    "Transonic",
    "boost",
    "include",
    "make_signature",
    "path_data_tests",
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
