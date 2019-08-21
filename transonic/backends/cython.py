"""Cython Backend
==================


"""
import copy

from transonic.analyses import extast
from transonic.annotation import compute_pythran_type_from_type

from .backend import BackendAOT


def compute_cython_type_from_pythran_type(type_):

    if isinstance(type_, type):
        type_ = compute_pythran_type_from_type(type_)

    if type_.endswith("]"):
        start, end = type_.split("[", 1)
        if not start.startswith("np."):
            start = "np." + start
        return start + "_t[" + end

    if any(type_.endswith(str(number)) for number in (32, 64, 128)):
        return "np." + type_

    return "cython." + type_


class CythonBackend(BackendAOT):
    backend_name = "cython"
    suffix_header = ".pxd"
    keyword_export = "cpdef"

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
