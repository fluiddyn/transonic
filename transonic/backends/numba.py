from typing import Callable
from textwrap import dedent
import inspect
import gast as ast

from transonic.analyses import extast

from .backend import BackendJIT


class NumbaBackend(BackendJIT):
    backend_name = "numba"


def get_source_with_numba(func: Callable):
    """Get the source and adapt to numba"""
    src = inspect.getsource(func)
    src = dedent(src)
    mod = extast.parse(src)
    for node in mod.body:
        node.decorator_list[0].keywords = [
            ast.keyword("nopython", value=ast.Str("True")),
            ast.keyword("nogil", value=ast.Str("True")),
        ]
    src = "\nfrom numba import jit \n" + extast.unparse(mod) + "\n"
    return src
