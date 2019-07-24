from pathlib import Path
from tokenize import tokenize, untokenize, NAME, OP
from io import BytesIO

from typing import Iterable, Optional
from warnings import warn

from transonic.analyses import extast, analyse_aot

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

    # overrited in childs
    def make_backend_file(self, path, analyse, force=None):
        raise RuntimeError
        return "Parent"

    def prepare_backend_file(self, path_py, force=False, log_level=None):
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
        path_backend = path_dir / path_py.name

        if not has_to_build(path_backend, path_py) and not force:
            logger.warning(f"File {path_backend} already up-to-date.")
            return None, None, None

        return path_py, path_dir, path_backend

    def write_code(self, code_backend, code_ext, path_dir, path_backend, force):

        for file_name, code in code_ext["function"].items():
            path_ext_file = path_dir / (file_name + ".py")
            write_if_has_to_write(path_ext_file, code, logger.info)

        if self.backend_name == "pythran":
            for file_name, code in code_ext["classe"].items():
                path_ext_file = (
                    path_dir.parent / "__pythran__" / (file_name + ".py")
                )
                write_if_has_to_write(path_ext_file, code, logger.info)

        code_pythran_old = ""
        if path_backend.exists() and not force:
            with open(path_backend) as file:
                code_pythran_old = file.read()

        if code_pythran_old == code_backend:
            logger.warning(f"Code in file {path_backend} already up-to-date.")
            return False

        logger.debug(f"code_{self.backend_name}:\n{code_backend}")

        path_dir.mkdir(exist_ok=True)

        with open(path_backend, "w") as file:
            file.write("".join(code_backend))

        logger.info(f"File {path_backend} written")

        return True

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
