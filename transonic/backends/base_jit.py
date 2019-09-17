"""SubBackend class for Transonic JIT compilation
=================================================

Internal API
------------

.. autoclass:: SubBackendJIT
   :members:
   :private-members:

"""

import re

try:
    import numpy as np
except ImportError:
    np = None

from transonic.analyses import extast
from transonic.signatures import make_signatures_from_typehinted_func
from transonic.log import logger
from transonic import mpi
from transonic.typing import format_type_as_backend_type, typeof
from transonic.util import get_source_without_decorator

from .for_classes import produce_code_class


class SubBackendJIT:
    """Sub-class for Transonic JIT compilation"""

    def __init__(self, name, type_formatter):
        self.name = name
        self.name_capitalized = name.capitalize()
        self.type_formatter = type_formatter

    def make_backend_source(self, info_analysis, func, path_backend):
        func_name = func.__name__
        jitted_dicts = info_analysis["jitted_dicts"]
        src = info_analysis["codes_dependance"][func_name]
        if func_name in info_analysis["special"]:
            if func_name in jitted_dicts["functions"]:
                src += extast.unparse(jitted_dicts["functions"][func_name])
            elif func_name in jitted_dicts["methods"]:
                src += extast.unparse(jitted_dicts["methods"][func_name])
        else:
            # TODO find a prettier solution to remove decorator for cython
            # than doing two times a regex
            src += re.sub(
                r"@.*?\sdef\s", "def ", get_source_without_decorator(func)
            )
        has_to_write = True
        if path_backend.exists() and mpi.rank == 0:
            with open(path_backend) as file:
                src_old = file.read()
            if src_old == src:
                has_to_write = False

        return src, has_to_write

    def make_new_header(self, func, arg_types):
        # Include signature comming from type hints
        signatures = make_signatures_from_typehinted_func(
            func, self.type_formatter
        )
        exports = set(f"export {signature}" for signature in signatures)

        if arg_types != "no types":
            exports.add(f"export {func.__name__}({', '.join(arg_types)})")
        return exports

    def merge_old_and_new_header(self, path_backend_header, header, func):

        try:
            path_backend_header_exists = path_backend_header.exists()
        except TimeoutError:
            raise RuntimeError(
                f"A MPI communication in Transonic failed when compiling "
                f"function {func}. This usually arises when a jitted "
                "function has to be compiled in MPI and is only called "
                f"by one process (rank={mpi.rank})."
            )

        if path_backend_header_exists:
            # get the old signature(s)
            header_old = self._load_old_header(path_backend_header)
            # FIXME: what do we do with the old signatures?
            header = self._merge_header_objects(header, header_old)

        return self._make_header_code(header)

    def _load_old_header(self, path_backend_header):
        exports_old = None
        if mpi.rank == 0:
            with open(path_backend_header) as file:
                exports_old = [export.strip() for export in file.readlines()]
        exports_old = mpi.bcast(exports_old)
        return exports_old

    def _merge_header_objects(self, header, header_old):
        header.update(header_old)
        return header

    def _make_header_code(self, header):
        return "\n".join(sorted(header)) + "\n"

    def write_new_header(self, path_backend_header, header, arg_types):
        mpi.barrier()
        if mpi.rank == 0:
            logger.debug(
                f"write {self.name_capitalized} signature in file "
                f"{path_backend_header} with types\n{arg_types}"
            )
            with open(path_backend_header, "w") as file:
                file.write(header)
                file.flush()

    def compute_typename_from_object(self, obj: object):
        """return the backend type name"""
        transonic_type = typeof(obj)
        return format_type_as_backend_type(transonic_type, self.type_formatter)

    def produce_code_class(self, cls):
        return produce_code_class(cls)
