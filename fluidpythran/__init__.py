from ._version import __version__
from .justintime import cachedjit, used_by_cachedjit, set_compile_cachedjit

try:
    from ._path_data_tests import path_data_tests
except ImportError:
    pass

from .annotation import Array, NDim, Type, Shape

from .aheadoftime import FluidPythran, pythran_def, boost, make_signature, include

from .util import set_pythranize_at_import
from .pythranizer import wait_for_all_extensions

__all__ = [
    "__version__",
    "FluidPythran",
    "pythran_def",
    "boost",
    "include",
    "make_signature",
    "path_data_tests",
    "Array",
    "NDim",
    "Type",
    "Shape",
    "cachedjit",
    "used_by_cachedjit",
    "set_compile_cachedjit",
    "set_pythranize_at_import",
    "wait_for_all_extensions",
]
