"""Cython Backend
==================


"""
from pathlib import Path
import gast as ast

from transonic.analyses import analyse_aot, extast
from transonic.analyses.util import print_dumped

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

    def make_backend_file(self, path_py, analyse, force=False, log_level=None):
        """Create a Python file from a Python file (if necessary)"""

        path_py, path_dir, _ = super().prepare_backend_file(
            path_py, force, log_level
        )

        if not analyse:
            with open(path_py) as f:
                code = f.read()
            analyse = analyse_aot(code, path_py)

        path_cython = (path_dir / path_py.name).with_suffix(".pyx")
        code_cython, code_ext = self.make_cython_code(path_py, analyse)

        if not code_cython:
            return

        super().write_code(code_cython, code_ext, path_dir, path_cython, force)

    def make_cython_code(self, path_py, analyse):

        boosted_dicts, code_dependance, annotations, blocks, code_ext = analyse
        boosted_dicts = dict(
            functions=boosted_dicts["functions"]["cython"],
            functions_ext=boosted_dicts["functions_ext"]["cython"],
            methods=boosted_dicts["methods"]["cython"],
            classes=boosted_dicts["classes"]["cython"],
        )

        code = ["\n" + code_dependance + "\n"]
        for func_name, fdef in boosted_dicts["functions"].items():
            signatures_func = set()
            try:
                ann = annotations["functions"][func_name]
            except KeyError:
                pass
            # else:
            #     typess = compute_pythran_types_from_valued_types(ann.values())

            #     for types in typess:
            #         signatures_func.add(
            #             f"# pythran export {func_name}({', '.join(types)})"
            #         )

            anns = annotations["comments"][func_name]
            # change annotations
            for name in fdef.args.args:
                if name.annotation:
                    name.id = name.annotation.id + " " + name.id

            # change type hints into cdef
            for index, node in enumerate(fdef.body):
                if isinstance(node, ast.AnnAssign):
                    cdef = "cdef " + node.annotation.id + " " + node.target.id
                    fdef.body[index] = extast.CommentLine(s=cdef)

            code.append(extast.unparse(fdef))

        return code, code_ext
