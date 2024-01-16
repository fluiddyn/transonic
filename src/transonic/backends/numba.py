"""Numba backend
================

Internal API
------------

.. autoclass:: SubBackendJITNumba
   :members:
   :private-members:

.. autoclass:: NumbaBackend
   :members:
   :private-members:

"""

from typing import Optional

from transonic.analyses.extast import parse, unparse, CommentLine, gast
from transonic.util import format_str

from .py import PythonBackend, SubBackendJITPython


def add_numba_comments(code):
    """Add Numba code in Python comments"""
    mod = parse(code)
    new_body = [CommentLine("# __protected__ from numba import njit")]

    for node in mod.body:
        if isinstance(node, gast.FunctionDef):
            new_body.append(
                CommentLine("# __protected__ @njit(cache=True, fastmath=True)")
            )
        new_body.append(node)

    mod.body = new_body
    return format_str(unparse(mod))


class SubBackendJITNumba(SubBackendJITPython):
    def make_backend_source(self, info_analysis, func, path_backend):
        src, has_to_write = super().make_backend_source(
            info_analysis, func, path_backend
        )

        if not src:
            return src, has_to_write

        return add_numba_comments(src), has_to_write


class NumbaBackend(PythonBackend):
    """Main class for the Numba backend"""

    backend_name = "numba"
    _SubBackendJIT = SubBackendJITNumba

    def compile_extension(
        self,
        path_backend,
        name_ext_file=None,
        native=False,
        xsimd=False,
        openmp=False,
        str_accelerator_flags: Optional[str] = None,
        parallel=True,
        force=True,
    ):
        if name_ext_file is None:
            name_ext_file = self.name_ext_from_path_backend(path_backend)

        with open(path_backend) as file:
            source = file.read()

        source = source.replace("# __protected__ ", "")

        with open(path_backend.with_name(name_ext_file), "w") as file:
            file.write(format_str(source))

        compiling = False
        process = None
        return compiling, process

    def _make_backend_code(self, path_py, analysis, **kwargs):
        """Create a backend code from a Python file"""
        code, codes_ext, header = super()._make_backend_code(path_py, analysis)

        if not code:
            return code, codes_ext, header

        code = add_numba_comments(code)

        for_meson = kwargs.get("for_meson", False)
        if for_meson:
            code = format_str(code.replace("# __protected__ ", ""))

        return code, codes_ext, header
