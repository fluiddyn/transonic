"""Cython Backend
==================


"""
from pathlib import Path
import gast as ast

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
    suffix_backend = ".pyx"

    def get_signatures(self, func_name, fdef, annotations):

        signatures_func = set()
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
                signatures_func.add("".join(ctypedef))
            # change function parameters
            for name in fdef.args.args:
                name.id = name_args[0] + " " + name.id
                del name_args[0]
        return signatures_func, fdef
