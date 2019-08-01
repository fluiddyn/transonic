from tokenize import tokenize, untokenize, NAME, OP
from io import BytesIO
from pathlib import Path
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

        if self.backend_name == "pythran":
            code_backend, code_ext = self.make_backend_code(path_py, analyse)
        elif self.backend_name == "cython":
            path_backend_pxd = (path_dir / path_py.name).with_suffix(".pxd")
            code_backend, code_ext, code_signature = self.make_backend_code(
                path_py, analyse
            )

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
        if self.backend_name == "cython":
            with open(path_backend_pxd, "w") as file:
                file.write("".join(code_signature))
        logger.info(f"File {path_backend} written")

        return path_backend

    def get_code_function(self, fdef):

        transformed = TypeHintRemover().visit(fdef)
        # convert the AST back to source code
        code = extast.unparse(transformed)

        code = format_str(code)

        return code

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
        signature_pxd = []
        # Deal with functions
        for func_name, fdef in boosted_dicts["functions"].items():

            code_function = self.get_code_function(fdef)
            signatures_func = self.get_signatures(func_name, fdef, annotations)
            if self.backend_name == "pythran":
                code.append("\n".join(sorted(signatures_func)))
            elif self.backend_name == "cython":
                if signatures_func:
                    signature_pxd = signature_pxd + signatures_func
            code.append(code_function)

        # Deal with methods
        signature, code_for_meths = self.get_code_meths(
            boosted_dicts, annotations, path_py
        )
        code = code + code_for_meths
        if signature:
            signature_pxd = signature_pxd + signature

        # Deal with blocks

        signature, code_blocks = self.get_code_blocks(blocks)
        code += code_blocks
        if signature:
            signature_pxd += signature

        code = "\n".join(code).strip()

        if code:
            code += (
                "\n\n# pythran export __transonic__\n"
                f"__transonic__ = ('{transonic.__version__}',)"
            )

        if self.backend_name != "cython":
            code = format_str(code)

        if self.backend_name == "cython":
            return code, code_ext, signature_pxd

        return code, code_ext

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

    def get_code_blocks(self, blocks):
        code = []
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
        return "", code
