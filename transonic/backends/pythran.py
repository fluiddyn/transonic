"""Pythran Backend
==================


"""


from pathlib import Path

from typing import Iterable, Optional
from warnings import warn

# from token import tok_name
from textwrap import indent


try:
    import black
except ImportError:
    black = False

import transonic
from .backend import Backend

from transonic.annotation import compute_pythran_types_from_valued_types

from transonic.analyses import analyse_aot
from transonic.analyses import extast

from transonic.log import logger

from transonic.util import (
    has_to_build,
    get_source_without_decorator,
    format_str,
    write_if_has_to_write,
)


class PythranBackend(Backend):
    backend_name = "pythran"

    def get_signatures(self, func_name, fdef, annotations):

        signatures_func = set()
        try:
            ann = annotations["functions"][func_name]
        except KeyError:
            pass
        else:
            typess = compute_pythran_types_from_valued_types(ann.values())
            for types in typess:
                signatures_func.add(
                    f"# pythran export {func_name}({', '.join(types)})"
                )

        anns = annotations["comments"][func_name]
        if not fdef.args.args:
            signatures_func.add(f"# pythran export {func_name}()")
        for ann in anns:
            typess = compute_pythran_types_from_valued_types(ann.values())

            for types in typess:
                signatures_func.add(
                    f"# pythran export {func_name}({', '.join(types)})"
                )
        return signatures_func, fdef
