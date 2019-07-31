"""Cython Backend
==================


"""
import copy
from pathlib import Path
import gast as ast
from textwrap import indent

from typing import Iterable, Optional
from warnings import warn

from transonic.analyses import analyse_aot, extast
from transonic.analyses.util import print_dumped
from transonic.annotation import compute_pythran_types_from_valued_types

from transonic.util import (
    has_to_build,
    get_source_without_decorator,
    format_str,
    write_if_has_to_write,
)

from transonic.log import logger

from .backend import Backend


class CythonBackend(Backend):
    backend_name = "cython"
    special_methods = ["__call__"]

    def get_signatures(self, func_name, fdef, annotations):
        fdef2 = copy.deepcopy(fdef)
        signatures_func = []
        try:
            ann = annotations["functions"][func_name]
        except KeyError:
            pass
        else:
            # produce ctypedef
            typess = compute_pythran_types_from_valued_types(ann.values())
            index = 0
            name_args = []
            for arg, value in ann.items():
                ctypedef = []
                name_arg = "__" + func_name + "_" + arg
                name_args.append(name_arg)
                ctypedef.append(f"ctypedef fused {name_arg}:\n")
                possible_types = [x[index] for x in typess]
                for possible_type in list(set(possible_types)):
                    ctypedef.append(f"   {possible_type}\n")
                index += 1
                signatures_func.append("".join(ctypedef))
            # change function parameters
            for name in fdef2.args.args:
                name.id = name_args[0] + " " + name.id
                del name_args[0]
            # fdef2 = self.change_inner_annotations(fdef2)
        signatures_func.append(
            "c" + self.get_code_function(fdef2)[2:].splitlines()[0][:-1]
        )
        return signatures_func

    def get_code_meths(self, boosted_dicts, annotations, path_py):

        init_funcs = self.get_init_functions(path_py)

        code = []
        signature_pxd = []
        previous_cls = ""
        for (class_name, meth_name), meth in boosted_dicts["methods"].items():
            if previous_cls != class_name:
                signature_pxd.append(f"cdef class {class_name}:")
                code.append(f"class {class_name}:")
            if class_name in init_funcs.keys():
                code.append(indent(init_funcs[class_name], prefix="    "))
                del init_funcs[class_name]
            previous_cls = class_name
            # meth = self.change_inner_annotations(meth)
            if meth_name not in self.special_methods:
                signature_pxd.append(
                    indent(
                        "c" + extast.unparse(meth)[2:].splitlines(0)[0][:-1],
                        prefix="    ",
                    )
                )
                code.append(indent(extast.unparse(meth), prefix="    "))
            else:
                code.append(indent(extast.unparse(meth)[2:], prefix="    "))
        return signature_pxd, code

    def change_inner_annotations(self, fdef):
        # change type hints into cdef
        for index, node in enumerate(fdef.body):
            if isinstance(node, ast.AnnAssign):
                cdef = "cdef " + node.annotation.id + " " + node.target.id
                if node.value:
                    cdef = cdef + "=" + extast.unparse(node.value)
                fdef.body[index] = extast.CommentLine(s=cdef)
        return fdef

    def get_init_functions(self, path_py: Path):
        init_funcs = dict()
        with open(path_py) as file:
            content = file.read()
        mod = extast.parse(content)
        for node in mod.body:
            if isinstance(node, ast.ClassDef):
                for sub_node in node.body:
                    if isinstance(sub_node, ast.FunctionDef):
                        if sub_node.name == "__init__":
                            init_funcs[node.name] = extast.unparse(sub_node)
        return init_funcs
