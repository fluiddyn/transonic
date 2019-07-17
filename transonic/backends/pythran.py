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
    def __init__(self):
        pass

    def make_backend_files(
        self,
        paths_py,
        force=False,
        log_level=None,
        mocked_modules: Optional[Iterable] = None,
        backend=None,
    ):
        """Create Pythran files from a list of Python files"""

        assert backend is None

        if mocked_modules is not None:
            warn(
                "The argument mocked_modules is deprecated. "
                "It is now useless for Transonic.",
                DeprecationWarning,
            )

        if log_level is not None:
            logger.set_level(log_level)

        paths_out = []
        for path in paths_py:
            path_out = self.make_pythran_file(path, force=force)
            if path_out:
                paths_out.append(path_out)

        if paths_out:
            nb_files = len(paths_out)
            if nb_files == 1:
                conjug = "s"
            else:
                conjug = ""

            logger.warning(
                f"{nb_files} files created or updated need{conjug}"
                " to be pythranized"
            )

        return paths_out

    def make_pythran_file(self, path_py: Path, force=False, log_level=None):
        """Create a Python file from a Python file (if necessary)"""
        if log_level is not None:
            logger.set_level(log_level)

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

        path_dir = path_py.parent / "__pythran__"
        path_pythran = path_dir / path_py.name

        if not has_to_build(path_pythran, path_py) and not force:
            logger.warning(f"File {path_pythran} already up-to-date.")
            return

        code_pythran, code_ext = self.make_pythran_code(path_py)

        if not code_pythran:
            return

        for file_name, code in code_ext["function"].items():
            path_ext_file = path_dir / (file_name + ".py")
            write_if_has_to_write(path_ext_file, code, logger.info)

        for file_name, code in code_ext["classe"].items():
            path_ext_file = path_dir.parent / "__pythran__" / (file_name + ".py")
            write_if_has_to_write(path_ext_file, code, logger.info)

        if path_pythran.exists() and not force:
            with open(path_pythran) as file:
                code_pythran_old = file.read()

            if code_pythran_old == code_pythran:
                logger.warning(f"Code in file {path_pythran} already up-to-date.")
                return

        logger.debug(f"code_pythran:\n{code_pythran}")

        path_dir.mkdir(exist_ok=True)

        with open(path_pythran, "w") as file:
            file.write(code_pythran)

        logger.info(f"File {path_pythran} written")

        return path_pythran

    def make_pythran_code(self, path_py):
        """Create a pythran code from a Python file"""
        with open(path_py) as file:
            code_module = file.read()

        boosted_dicts, code_dependance, annotations, blocks, code_ext = analyse_aot(
            code_module, path_py
        )

        code = ["\n" + code_dependance + "\n"]

        for func_name, fdef in boosted_dicts["functions"].items():

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

            code.append("\n".join(sorted(signatures_func)))

            code.append(self.get_code_function(fdef))

        for (class_name, meth_name), fdef in boosted_dicts["methods"].items():

            class_def = boosted_dicts["classes"][class_name]

            if class_name in annotations["classes"]:
                annotations_class = annotations["classes"][class_name]
            else:
                annotations_class = {}

            if (class_name, meth_name) in annotations["methods"]:
                annotations_meth = annotations["methods"][(class_name, meth_name)]
            else:
                annotations_meth = {}

            code_for_meth = self.produce_code_for_method(
                fdef, class_def, annotations_meth, annotations_class
            )

            code.append(code_for_meth)

        for block in blocks:
            signatures_block = set()
            for ann in block.signatures:
                typess = compute_pythran_types_from_valued_types(ann.values())

                for types in typess:
                    signatures_block.add(
                        f"# pythran export {block.name}({', '.join(types)})"
                    )

            code.extend(sorted(signatures_block))

            str_variables = ", ".join(block.signatures[0].keys())

            code.append(f"\ndef {block.name}({str_variables}):\n")

            code_block = indent(extast.unparse(block.ast_code), "    ")

            code.append(code_block)

            if block.results:
                code.append(f"    return {', '.join(block.results)}\n")

        arguments_blocks = {
            block.name: list(block.signatures[0].keys()) for block in blocks
        }

        if arguments_blocks:
            code.append(
                "# pythran export arguments_blocks\n"
                f"arguments_blocks = {str(arguments_blocks)}\n"
            )

        code = "\n".join(code).strip()

        if code:
            code += (
                "\n\n# pythran export __transonic__\n"
                f"__transonic__ = ('{transonic.__version__}',)"
            )

        code = format_str(code)

        return code, code_ext

    def produce_code_for_method(
        self, fdef, class_def, annotations_meth, annotations_class, jit=False
    ):

        class_name = class_def.name
        meth_name = fdef.name

        new_code, attributes, name_new_func = self.produce_new_code_method(
            fdef, class_def
        )

        types_attrs = []

        for attr in attributes:
            if attr not in annotations_class:
                raise NotImplementedError(
                    f"self.{attr} used but {attr} not in class annotations"
                )
        types_attrs = [annotations_class[attr] for attr in attributes]

        types_func = list(annotations_meth.values())

        types_pythran = types_attrs + types_func

        try:
            types_string_signatures = compute_pythran_types_from_valued_types(
                types_pythran
            )
        except ValueError:
            if jit:
                types_string_signatures = []
            else:
                raise

        pythran_signatures = set()

        for types_string_signature in types_string_signatures:
            pythran_signatures.add(
                "# pythran export "
                + name_new_func
                + "("
                + ", ".join(types_string_signature)
                + ")\n"
            )

        if jit:
            new_code = "from transonic import jit\n\n@jit\n" + new_code

        python_code = "\n".join(sorted(pythran_signatures)) + "\n" + new_code

        str_self_dot_attributes = ", ".join("self." + attr for attr in attributes)
        args_func = [arg.id for arg in fdef.args.args[1:]]
        str_args_func = ", ".join(args_func)

        defaults = fdef.args.defaults
        nb_defaults = len(defaults)
        nb_args = len(fdef.args.args)
        nb_no_defaults = nb_args - nb_defaults - 1

        str_args_value_func = []
        ind_default = 0
        for ind, arg in enumerate(fdef.args.args[1:]):
            name = arg.id
            if ind < nb_no_defaults:
                str_args_value_func.append(f"{name}")
            else:
                default = extast.unparse(defaults[ind_default]).strip()
                str_args_value_func.append(f"{name}={default}")
                ind_default += 1

        str_args_value_func = ", ".join(str_args_value_func)

        if str_self_dot_attributes:
            str_args_pythran_func = ", ".join(
                (str_self_dot_attributes, str_args_func)
            )
        else:
            str_args_pythran_func = str_args_func

        if jit:
            name_new_method = f"__new_method__{class_name}__{meth_name}"
            python_code += (
                f"\ndef {name_new_method}"
                f"(self, {str_args_value_func}):\n"
                f"    return {name_new_func}({str_args_pythran_func})"
                "\n"
            )
        else:
            name_var_code_new_method = (
                f"__code_new_method__{class_name}__{meth_name}"
            )
            python_code += (
                f"\n# pythran export {name_var_code_new_method}\n"
                f'\n{name_var_code_new_method} = """\n\n'
                f"def new_method(self, {str_args_value_func}):\n"
                f"    return pythran_func({str_args_pythran_func})"
                '\n\n"""\n'
            )

        python_code = format_str(python_code)

        return python_code
