"""numba Backend
==================


"""
from pathlib import Path

from transonic.analyses import analyse_aot
from transonic.analyses import extast

from transonic.util import (
    has_to_build,
    get_source_without_decorator,
    format_str,
    write_if_has_to_write,
)

from transonic.log import logger

from .backend import Backend


class NumbaBackend(Backend):
    def __init__(self, paths_py):
        super.__init__(paths_py)

    def make_backend_files(self):
        """Create numba files from a list of Python files"""
        paths_out = []
        for path in self.paths_py:
            path_out = self.make_numba_file(path)
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

    def make_numba_file(self, path_py: Path, force="force", log_level=None):
        if log_level is not None:
            logger.set_level(log_level)

        path_py = Path(path_py)

        if not path_py.exists():
            raise FileNotFoundError(f"Input file {path_py} not found")

        if path_py.absolute().parent.name == "__numba__":
            logger.debug(f"skip file {path_py}")
            return
        if not path_py.name.endswith(".py"):
            raise ValueError(
                "transonic only processes Python file. Cannot process {path_py}"
            )
        path_dir = path_py.parent / "__pythran__"
        path_numba = path_dir / path_py.name

        if not has_to_build(path_numba, path_py) and not force:
            logger.warning(f"File {path_numba} already up-to-date.")
            return

        code_pythran, code_ext = self.make_numba_code(path_py)

        if not code_pythran:
            return

        for file_name, code in code_ext["function"].items():
            path_ext_file = path_dir / (file_name + ".py")
            write_if_has_to_write(path_ext_file, code, logger.info)

        for file_name, code in code_ext["classe"].items():
            path_ext_file = path_dir.parent / "__pythran__" / (file_name + ".py")
            write_if_has_to_write(path_ext_file, code, logger.info)

        if path_numba.exists() and not force:
            with open(path_numba) as file:
                code_pythran_old = file.read()

            if code_pythran_old == code_pythran:
                logger.warning(f"Code in file {path_numba} already up-to-date.")
                return

        logger.debug(f"code_pythran:\n{code_pythran}")

        path_dir.mkdir(exist_ok=True)

        with open(path_numba, "w") as file:
            file.write(code_pythran)

        logger.info(f"File {path_numba} written")

        return path_numba

    def make_numba_code(self, path_py):
        """Create a pythran code from a Python file"""
        with open(path_py) as file:
            code_module = file.read()

        boosted_dicts, code_dependance, annotations, blocks, code_ext = analyse_aot(
            code_module, path_py
        )

        print(boosted_dicts)
