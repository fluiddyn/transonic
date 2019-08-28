"""Base class for the Transonic backends
========================================

Internal API
------------

.. autoclass:: Backend
   :members:
   :private-members:

"""

from pathlib import Path
from textwrap import indent
from typing import Iterable, Optional

import transonic

from transonic.analyses import extast, analyse_aot
from transonic.annotation import compute_signatures_from_typeobjects
from transonic.log import logger
from transonic.compiler import compile_extension, ext_suffix
from transonic import mpi
from transonic.mpi import PathSeq

from transonic.util import (
    has_to_build,
    format_str,
    write_if_has_to_write,
    TypeHintRemover,
    make_hex,
)

from .base_jit import SubBackendJIT
from .for_classes import make_new_code_method_from_nodes


def _make_code_from_fdef_node(fdef, black=True):
    transformed = TypeHintRemover().visit(fdef)
    # convert the AST back to source code
    code = extast.unparse(transformed)
    return format_str(code)


class Backend:
    """Base class for the Transonic backends"""

    backend_name = "base"
    suffix_backend = ".py"
    suffix_header = None
    suffix_extension = ext_suffix
    keyword_export = "export"
    _SubBackendJIT = SubBackendJIT
    needs_compilation = True

    def __init__(self):
        self.name = self.backend_name
        self.name_capitalized = self.name.capitalize()
        self.jit = self._SubBackendJIT(self.name)

    def make_backend_files(
        self, paths_py, force=False, log_level=None, backend=None
    ):
        """Create backend files from a list of Python files"""
        if backend is not None:
            raise NotImplementedError

        if log_level is not None:
            logger.set_level(log_level)

        paths_out = []
        for path in paths_py:
            with open(path) as file:
                code = file.read()
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

            if self.needs_compilation:
                logger.warning(
                    f"{nb_files} files created or updated need{conjug}"
                    f" to be {self.name}ized"
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

        if path_py.absolute().parent.name == f"__{self.name}__":
            logger.debug(f"skip file {path_py}")
            return None, None, None
        if not path_py.name.endswith(".py"):
            raise ValueError(
                "transonic only processes Python file. Cannot process {path_py}"
            )

        path_dir = path_py.parent / str(f"__{self.name}__")
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

        code_backend, codes_ext, code_header = self._make_backend_code(
            path_py, analyse
        )
        if not code_backend:
            return
        logger.debug(f"code_{self.name}:\n{code_backend}")

        for file_name, code in codes_ext["function"].items():
            path_ext_file = path_dir / (file_name + ".py")
            write_if_has_to_write(
                path_ext_file, format_str(code), logger.info, force
            )

        for file_name, code in codes_ext["class"].items():
            path_ext_file = (
                path_dir.parent / f"__{self.name}__" / (file_name + ".py")
            )
            write_if_has_to_write(
                path_ext_file, format_str(code), logger.info, force
            )

        written = write_if_has_to_write(
            path_backend, code_backend, logger.info, force
        )

        if not written:
            logger.warning(f"Code in file {path_backend} already up-to-date.")
            return

        if self.suffix_header:
            path_header = (path_dir / path_py.name).with_suffix(
                self.suffix_header
            )
            write_if_has_to_write(path_header, code_header, logger.info, force)

        logger.info(f"File {path_backend} updated")

        return path_backend

    def _make_first_lines_header(self):
        return []

    def _make_backend_code(self, path_py, analyse):
        """Create a backend code from a Python file"""

        boosted_dicts, code_dependance, annotations, blocks, codes_ext = analyse

        boosted_dicts = dict(
            functions=boosted_dicts["functions"][self.name],
            functions_ext=boosted_dicts["functions_ext"][self.name],
            methods=boosted_dicts["methods"][self.name],
            classes=boosted_dicts["classes"][self.name],
        )

        lines_code = ["\n" + code_dependance + "\n"]
        lines_header = self._make_first_lines_header()
        # Deal with functions
        for fdef in boosted_dicts["functions"].values():
            signatures_func = self._make_header_1_function(fdef, annotations)
            if signatures_func:
                lines_header.extend(signatures_func)
            code_function = _make_code_from_fdef_node(fdef)
            lines_code.append(code_function)

        # Deal with methods
        signatures, code_for_meths = self._make_code_methods(
            boosted_dicts, annotations, path_py
        )
        lines_code.extend(code_for_meths)
        if signatures:
            lines_header.extend(signatures)

        # Deal with blocks
        signatures, code_blocks = self._make_code_blocks(blocks)
        lines_code.extend(code_blocks)
        if signatures:
            lines_header.extend(signatures)

        code = "\n".join(lines_code).strip()

        if code:
            self._append_line_header_variable(lines_header, "__transonic__")
            code += f"\n\n__transonic__ = ('{transonic.__version__}',)"

        return format_str(code), codes_ext, "\n".join(lines_header).strip() + "\n"

    def _append_line_header_variable(self, lines_header, name_variable):
        pass

    def _make_code_blocks(self, blocks):
        code = []
        signatures_blocks = []
        for block in blocks:

            signatures_as_lists_strings = []
            for annot in block.signatures:
                signatures_as_lists_strings.extend(
                    compute_signatures_from_typeobjects(annot)
                )

            str_variables = ", ".join(block.signatures[0].keys())
            fdef_block = extast.ast.parse(
                f"""def {block.name}({str_variables}):pass"""
            ).body[0]

            # TODO: locals_types for blocks
            locals_types = None
            signatures_blocks.extend(
                self._make_header_from_fdef_signatures(
                    fdef_block, signatures_as_lists_strings, locals_types
                )
            )

            code.append(f"\ndef {block.name}({str_variables}):\n")
            code.append(indent(extast.unparse(block.ast_code), "    "))
            if block.results:
                code.append(f"    return {', '.join(block.results)}\n")

        arguments_blocks = {
            block.name: list(block.signatures[0].keys()) for block in blocks
        }

        if arguments_blocks:
            self._append_line_header_variable(
                signatures_blocks, "arguments_blocks"
            )
            code.append(f"arguments_blocks = {str(arguments_blocks)}\n")
        return signatures_blocks, code

    def _make_code_methods(self, boosted_dicts, annotations, path_py):
        meths_code = []
        header_lines = []
        for (class_name, meth_name), fdef in boosted_dicts["methods"].items():
            signatures, code_for_meth = self._make_code_method(
                class_name, fdef, meth_name, annotations, boosted_dicts
            )
            meths_code.append(code_for_meth)
            header_lines.extend(signatures)
        return header_lines, meths_code

    def _make_code_method(
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

        meth_name = fdef.name
        python_code, attributes, _ = make_new_code_method_from_nodes(
            class_def, fdef
        )

        for attr in attributes:
            if attr not in annotations_class:
                raise NotImplementedError(
                    f"self.{attr} used but {attr} not in class annotations"
                )
        types_attrs = [annotations_class[attr] for attr in attributes]
        types_func = list(annotations_meth.values())
        types_pythran = types_attrs + types_func
        signatures_as_lists_strings = compute_signatures_from_typeobjects(
            types_pythran
        )

        # TODO: locals_types for methods
        locals_types = None
        signatures_method = self._make_header_from_fdef_signatures(
            extast.parse(python_code).body[0],
            signatures_as_lists_strings,
            locals_types,
        )

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
            str_args_backend_func = ", ".join(
                (str_self_dot_attributes, str_args_func)
            )
        else:
            str_args_backend_func = str_args_func

        name_var_code_new_method = f"__code_new_method__{class_name}__{meth_name}"

        self._append_line_header_variable(
            signatures_method, name_var_code_new_method
        )
        python_code += (
            f'\n{name_var_code_new_method} = """\n\n'
            f"def new_method(self, {str_args_value_func}):\n"
            f"    return backend_func({str_args_backend_func})"
            '\n\n"""\n'
        )

        return signatures_method, format_str(python_code)

    def _make_header_1_function(self, fdef, annotations):
        raise NotImplementedError

    def _make_header_from_fdef_signatures(
        self, fdef, signatures_as_lists_strings, locals_types=None
    ):
        raise NotImplementedError

    def name_ext_from_path_backend(self, path_backend):
        """Return an extension name given the path of a Pythran file"""

        name = None
        if mpi.rank == 0:
            path_backend = PathSeq(path_backend)
            if path_backend.exists():
                with open(path_backend) as file:
                    src = file.read()
                # quick fix to recompile when the header has been changed
                for suffix in (".pythran", ".pxd"):
                    path_header = path_backend.with_suffix(suffix)
                    if path_header.exists():
                        with open(path_header) as file:
                            src += file.read()
            else:
                src = ""

            name = path_backend.stem + "_" + make_hex(src) + self.suffix_extension

        return mpi.bcast(name)

    def compile_extensions(
        self,
        paths: Iterable[Path],
        str_pythran_flags: str,
        parallel=True,
        force=True,
    ):
        print("compile extension")
        for path in paths:
            self.compile_extension(
                path,
                str_pythran_flags=str_pythran_flags,
                parallel=parallel,
                force=force,
            )

    def compile_extension(
        self,
        path_backend,
        name_ext_file=None,
        native=False,
        xsimd=False,
        openmp=False,
        str_pythran_flags: Optional[str] = None,
        parallel=True,
        force=True,
    ):
        raise NotImplementedError


class BackendAOT(Backend):
    """Backend for ahead-of-time compilers"""

    def check_if_compiled(self, module):
        try:
            path = module.__file__
        except AttributeError:
            return True

        return not path.endswith(".py")

    def compile_extension(
        self,
        path_backend,
        name_ext_file=None,
        native=False,
        xsimd=False,
        openmp=False,
        str_pythran_flags: Optional[str] = None,
        parallel=True,
        force=True,
    ):
        if name_ext_file is None:
            name_ext_file = self.name_ext_from_path_backend(path_backend)

        compiling = True
        process = compile_extension(
            path_backend,
            self.name,
            name_ext_file,
            native=native,
            xsimd=xsimd,
            openmp=openmp,
            str_pythran_flags=str_pythran_flags,
            parallel=parallel,
            force=force,
        )
        return compiling, process

    def _make_header_1_function(self, fdef, annotations):

        try:
            annots = annotations["__in_comments__"][fdef.name]
        except KeyError:
            annots = []

        try:
            annot = annotations["functions"][fdef.name]
        except KeyError:
            pass
        else:
            annots.append(annot)

        signatures_as_lists_strings = []
        for annot in annots:
            signatures_as_lists_strings.extend(
                compute_signatures_from_typeobjects(annot)
            )

        try:
            locals_types = annotations["__locals__"][fdef.name]
        except KeyError:
            locals_types = None

        return self._make_header_from_fdef_signatures(
            fdef, signatures_as_lists_strings, locals_types
        )


class BackendJIT(Backend):
    """Backend for just-in-time compilers"""

    suffix_extension = ".py"
    needs_compilation = False

    def check_if_compiled(self, module):
        return True

    def _make_header_1_function(self, fdef, annotations):
        return []

    def _make_first_lines_header(self):
        return []

    def _make_header_from_fdef_signatures(
        self, fdef, signatures_as_lists_strings, locals_types=None
    ):
        return []
