import re

try:
    import numpy as np
except ImportError:
    np = None

from transonic.analyses import extast
from transonic.annotation import (
    make_signatures_from_typehinted_func,
    normalize_type_name,
)
from transonic.log import logger
from transonic import mpi
from transonic.util import get_source_without_decorator

from .for_classes import produce_code_class


class BackendJIT:
    def __init__(self, name):
        self.name = name
        self.name_capitalized = name.capitalize()

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
        signatures = make_signatures_from_typehinted_func(func)

        if self.name == "pythran":
            keyword = "export "
        elif self.name == "cython":
            keyword = "cpdef "
        exports = set(keyword + signature for signature in signatures)

        if arg_types != "no types":
            export_new = "{}{}({})".format(
                keyword, func.__name__, ", ".join(arg_types)
            )
            if export_new not in exports:
                exports.add(export_new)
        return exports

    def merge_old_and_new_header(self, path_backend_header, exports, func):

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

            exports_old = None
            if mpi.rank == 0:
                with open(path_backend_header) as file:
                    exports_old = [export.strip() for export in file.readlines()]
            exports_old = mpi.bcast(exports_old)

            # FIXME: what do we do with the old signatures?
            exports.update(exports_old)

        header = "\n".join(sorted(exports)) + "\n"

        return header

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
        """return the Pythran type name"""
        name = type(obj).__name__
        name = normalize_type_name(name)

        if np and isinstance(obj, np.ndarray):
            name = obj.dtype.name
            if obj.ndim != 0:
                name += "[" + ", ".join([":"] * obj.ndim) + "]"

        if name in ("list", "set", "dict"):
            if not obj:
                raise ValueError(
                    f"cannot determine the {self.name_capitalized} type from an empty {name}"
                )

        if name in ("list", "set"):
            item_type = type(obj[0])
            # FIXME: we could check if the iterable is homogeneous...
            name = item_type.__name__ + " " + name

        if name == "dict":
            for key, value in obj.items():
                break
            # FIXME: we could check if the dict is homogeneous...
            name = type(key).__name__ + ": " + type(value).__name__ + " dict"

        return name

    def produce_code_class(self, cls):
        return produce_code_class(cls)
