"""Cython Backend
==================


"""
import copy

from transonic.analyses import extast
from transonic.annotation import (
    compute_pythran_types_from_valued_types,
    compute_pythran_type_from_type,
)

from .backend import BackendAOT


def compute_cython_type_from_pythran_type(type_):

    if isinstance(type_, type):
        type_ = compute_pythran_type_from_type(type_)

    if type_.endswith("]"):
        start, end = type_.split("[")
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

    def _make_header_1_function(self, func_name, fdef, annotations):
        fdef = copy.deepcopy(fdef)
        signatures_func = []
        try:
            annot = annotations["functions"][func_name]
        except KeyError:
            pass
        else:
            # produce ctypedef
            typess = compute_pythran_types_from_valued_types(annot.values())
            index = 0
            name_type_args = []
            for arg in annot.keys():
                ctypedef = []
                name_type_arg = "__" + func_name + "_" + arg
                name_type_args.append(name_type_arg)
                ctypedef.append(f"ctypedef fused {name_type_arg}:\n")
                possible_types = [x[index] for x in typess]
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

        fdef.body = []
        fdef.decorator_list = []
        try:
            locals_types = annotations["__locals__"][func_name]
        except KeyError:
            pass
        else:
            locals_types = ", ".join(
                f"{k}={compute_cython_type_from_pythran_type(v)}"
                for k, v in locals_types.items()
            )
            signatures_func.append(f"@cython.locals({locals_types})\n")

        signatures_func.append("cp" + extast.unparse(fdef).strip()[:-1] + "\n")
        return signatures_func
