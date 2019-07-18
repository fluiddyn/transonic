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
    def __init__(self):
        pass

    def make_backend_file(self, path_py, analyse, force=None):
        """Create a Python file from a Python file (if necessary)"""
        # if log_level is not None:
        #     logger.set_level(log_level)

        path_py = Path(path_py)

        if not path_py.exists():
            raise FileNotFoundError(f"Input file {path_py} not found")

        if path_py.absolute().parent.name == "__pythran__":
            logger.debug(f"skip file {path_py}")
            return
        if not path_py.name.endswith(".py"):
            raise ValueError(
                "transonic only processes Python file. Cannot process {path_py}"
            )

        path_dir = path_py.parent / "__cython__"
        path_cython = (path_dir / path_py.name).with_suffix(".pyx")

        if not has_to_build(path_cython, path_py):  # and not force:
            logger.warning(f"File {path_cython} already up-to-date.")
            return

        code_cython, code_ext = self.make_cython_code(path_py, analyse)

        if not code_cython:
            return

        for file_name, code in code_ext["function"].items():
            path_ext_file = path_dir / (file_name + ".py")
            write_if_has_to_write(path_ext_file, code, logger.info)

        path_dir.mkdir(exist_ok=True)

        with open(path_cython, "w") as file:
            file.write("".join(code_cython))

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
            print_dumped(fdef.decorator_list)
            # change annotations
            if fdef.decorator_list:
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
