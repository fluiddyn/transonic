"""Cython Backend
==================


"""
import copy

from transonic.analyses import extast
from transonic.annotation import (
    compute_pythran_type_from_type,
    make_signatures_from_typehinted_func,
)

from .backend import BackendAOT
from .backend_jit import BackendJIT


def compute_cython_type_from_pythran_type(type_):

    if isinstance(type_, type):
        type_ = compute_pythran_type_from_type(type_)

    if type_.endswith("]"):
        start, end = type_.split("[", 1)
        if not start.startswith("np."):
            start = "np." + start

        dim = end.count("[") + 1
        if dim > 1:
            end = ",".join(":" * dim) + "]"

        if end == "]":
            end = ":]"

        return start + "_t[" + end

    if any(type_.endswith(str(number)) for number in (32, 64, 128)):
        return "np." + type_ + "_t"

    return "cython." + type_


class CythonJIT(BackendJIT):
    def compute_typename_from_object(self, obj: object):
        """return the Pythran type name"""
        return compute_cython_type_from_pythran_type(
            super().compute_typename_from_object(obj)
        )

    def make_new_header(self, func, arg_types):
        # Include signature comming from type hints
        signatures = make_signatures_from_typehinted_func(func)

    def _load_old_header(self, path_backend_header):
        pass
        # exports_old = None
        # if mpi.rank == 0:
        #     with open(path_backend_header) as file:
        #         exports_old = [export.strip() for export in file.readlines()]
        # exports_old = mpi.bcast(exports_old)
        # return exports_old

    def _merge_header_objects(self, header, header_old):
        pass
        # header.update(header_old)
        # return header

    def _make_header_code(self, header):
        return ""
        # return "\n".join(sorted(header)) + "\n"


class CythonBackend(BackendAOT):
    backend_name = "cython"
    suffix_header = ".pxd"
    keyword_export = "cpdef"
    _BackendJIT = CythonJIT

    def _make_first_lines_header(self):
        return ["import cython\n\nimport numpy as np\ncimport numpy as np\n"]

    def _make_header_from_fdef_signatures(
        self, fdef, signatures_as_lists_strings, locals_types=None
    ):

        fdef = extast.ast.FunctionDef(
            name=fdef.name,
            args=copy.deepcopy(fdef.args),
            body=[],
            decorator_list=[],
            returns=None,
        )
        signatures_func = []
        if signatures_as_lists_strings:
            # produce ctypedef
            index = 0
            name_type_args = []
            for arg in [name.id for name in fdef.args.args]:
                ctypedef = []
                name_type_arg = "__" + fdef.name + "_" + arg
                name_type_args.append(name_type_arg)
                ctypedef.append(f"ctypedef fused {name_type_arg}:\n")
                possible_types = [x[index] for x in signatures_as_lists_strings]
                for possible_type in list(set(possible_types)):
                    ctypedef.append(
                        f"   {compute_cython_type_from_pythran_type(possible_type)}\n"
                    )
                index += 1
                signatures_func.append("".join(ctypedef))

            # change function parameters
            for name in fdef.args.args:
                name.annotation = None
                name.id = name_type_args[0] + " " + name.id
                del name_type_args[0]

        if locals_types is not None and locals_types:
            # TODO: fused types not supported here
            locals_types = ", ".join(
                f"{k}={compute_cython_type_from_pythran_type(v)}"
                for k, v in locals_types.items()
            )
            signatures_func.append(f"@cython.locals({locals_types})\n")

        signatures_func.append("cp" + extast.unparse(fdef).strip()[:-1] + "\n")
        return signatures_func
