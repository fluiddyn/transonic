from pathlib import Path
from tokenize import tokenize, untokenize, NAME, OP
from io import BytesIO
from textwrap import indent

from typing import Iterable, Optional
from warnings import warn

import transonic

from transonic.analyses import extast, analyse_aot
from transonic.annotation import compute_pythran_types_from_valued_types

from transonic.log import logger

from ..util import (
    has_to_build,
    get_source_without_decorator,
    format_str,
    write_if_has_to_write,
    TypeHintRemover,
    format_str,
)


class Backend:
    backend_name = "base"
    suffix_backend = ".py"

    def make_backend_files(
        self,
        paths_py,
        force=False,
        log_level=None,
        mocked_modules: Optional[Iterable] = None,
        backend=None,
    ):
        """Create backend files from a list of Python files"""
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
            with open(path) as f:
                code = f.read()
            analyse = analyse_aot(code, path)
            path_out = self.make_backend_file(path, analyse, force=force)
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
                " to be {self.backend_name}ized"
            )

        return paths_out

    def make_backend_file(
        self, path_py: Path, analyse=None, force=False, log_level=None
    ):
        """Create a Python file from a Python file (if necessary)"""

        if log_level is not None:
            logger.set_level(log_level)

        path_py = Path(path_py)

        if not path_py.exists():
            raise FileNotFoundError(f"Input file {path_py} not found")

        if path_py.absolute().parent.name == "__" + self.backend_name + "__":
            logger.debug(f"skip file {path_py}")
            return None, None, None
        if not path_py.name.endswith(".py"):
            raise ValueError(
                "transonic only processes Python file. Cannot process {path_py}"
            )

        path_dir = path_py.parent / str("__" + self.backend_name + "__")
        path_backend = (path_dir / path_py.name).with_suffix(self.suffix_backend)

        if not has_to_build(path_backend, path_py) and not force:
            logger.warning(f"File {path_backend} already up-to-date.")
            return None, None, None

        if path_dir is None:
            return

        if not analyse:
            with open(path_py) as file:
                code = file.read()
            analyse = analyse_aot(code, path_py)

        code_backend, code_ext = self.make_backend_code(path_py, analyse)

        if not code_backend:
            return

        for file_name, code in code_ext["function"].items():
            path_ext_file = path_dir / (file_name + ".py")
            write_if_has_to_write(path_ext_file, code, logger.info)

        for file_name, code in code_ext["classe"].items():
            path_ext_file = (
                path_dir.parent / f"__{self.backend_name}__" / (file_name + ".py")
            )
            write_if_has_to_write(path_ext_file, code, logger.info)

        code_pythran_old = ""
        if path_backend.exists() and not force:
            with open(path_backend) as file:
                code_pythran_old = file.read()

        if code_pythran_old == code_backend:
            logger.warning(f"Code in file {path_backend} already up-to-date.")
            return

        logger.debug(f"code_{self.backend_name}:\n{code_backend}")

        path_dir.mkdir(exist_ok=True)

        with open(path_backend, "w") as file:
            file.write("".join(code_backend))

        logger.info(f"File {path_backend} written")

        return path_backend

    def get_code_meth(
        self, class_name, fdef, meth_name, annotations, boosted_dicts
    ):
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
        return code_for_meth

    def get_code_function(self, fdef):

        transformed = TypeHintRemover().visit(fdef)
        # convert the AST back to source code
        code = extast.unparse(transformed)

        code = format_str(code)

        return code

    def produce_new_code_method(self, fdef, class_def):

        src = self.get_code_function(fdef)

        tokens = []
        attributes = set()

        using_self = False

        g = tokenize(BytesIO(src.encode("utf-8")).readline)
        for toknum, tokval, a, b, c in g:
            # logger.debug((tok_name[toknum], tokval))

            if using_self == "self":
                if toknum == OP and tokval == ".":
                    using_self = tokval
                    continue
                elif toknum == OP and tokval in (",", ")"):
                    tokens.append((NAME, "self"))
                    using_self = False
                else:
                    raise NotImplementedError(
                        f"self{tokval} not supported by Transonic"
                    )

            if using_self == ".":
                if toknum == NAME:
                    using_self = False
                    tokens.append((NAME, "self_" + tokval))
                    attributes.add(tokval)
                    continue
                else:
                    raise NotImplementedError

            if toknum == NAME and tokval == "self":
                using_self = "self"
                continue

            tokens.append((toknum, tokval))

        attributes = sorted(attributes)

        attributes_self = ["self_" + attr for attr in attributes]

        index_self = tokens.index((NAME, "self"))

        tokens_attr = []
        for ind, attr in enumerate(attributes_self):
            tokens_attr.append((NAME, attr))
            tokens_attr.append((OP, ","))

        if tokens[index_self + 1] == (OP, ","):
            del tokens[index_self + 1]

        tokens = tokens[:index_self] + tokens_attr + tokens[index_self + 1 :]

        func_name = fdef.name

        index_func_name = tokens.index((NAME, func_name))
        name_new_func = f"__for_method__{class_def.name}__{func_name}"
        tokens[index_func_name] = (NAME, name_new_func)
        # change recusive calls
        if func_name in attributes:
            attributes.remove(func_name)
            index_rec_calls = [
                index
                for index, (name, value) in enumerate(tokens)
                if value == "self_" + func_name
            ]
            # delete the occurence of "self_" + func_name in function parameter
            del tokens[index_rec_calls[0] + 1]
            del tokens[index_rec_calls[0]]
            # consider the two deletes
            offset = -2
            # adapt all recurrence calls
            for ind in index_rec_calls[1:]:
                # adapt the index to the insertd and deletes
                ind += offset
                tokens[ind] = (tokens[ind][0], name_new_func)
                # put the attributes in parameter
                for attr in reversed(attributes):
                    tokens.insert(ind + 2, (1, ","))
                    tokens.insert(ind + 2, (1, "self_" + attr))
                # consider the inserts
                offset += len(attributes) * 2
        new_code = untokenize(tokens).decode("utf-8")

        return new_code, attributes, name_new_func

    def make_backend_code(self, path_py, analyse):
        """Create a backend code from a Python file"""

        boosted_dicts, code_dependance, annotations, blocks, code_ext = analyse

        boosted_dicts = dict(
            functions=boosted_dicts["functions"][self.backend_name],
            functions_ext=boosted_dicts["functions_ext"][self.backend_name],
            methods=boosted_dicts["methods"][self.backend_name],
            classes=boosted_dicts["classes"][self.backend_name],
        )

        code = ["\n" + code_dependance + "\n"]

        for func_name, fdef in boosted_dicts["functions"].items():

            signatures_func, boosted_dicts["functions"][
                func_name
            ] = self.get_signatures(func_name, fdef, annotations)

            code.append("\n".join(sorted(signatures_func)))
            code.append(self.get_code_function(fdef))

        for (class_name, meth_name), fdef in boosted_dicts["methods"].items():

            code_for_meth = self.get_code_meth(
                class_name, fdef, meth_name, annotations, boosted_dicts
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

        if self.backend_name != "cython":
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
