"""Internal utilities
=====================

Internal API
------------

.. autofunction:: get_module_name

.. autofunction:: modification_date

.. autofunction:: has_to_build

.. autofunction:: get_source_without_decorator

.. autoclass:: TypeHintRemover
   :members:
   :private-members:

.. autofunction:: strip_typehints

.. autofunction:: make_hex

.. autofunction:: get_ipython_input

.. autofunction:: get_info_from_ipython

.. autoclass:: SchedulerPopen
   :members:
   :private-members:

.. autofunction:: name_ext_from_path_pythran

.. autofunction:: compile_pythran_files

.. autofunction:: compile_pythran_file

.. autofunction:: has_to_pythranize_at_import

.. autofunction:: import_from_path

"""

import os
import sys
import inspect
from datetime import datetime
import re
from pathlib import Path
import ast
import hashlib
import sysconfig
import importlib.util

# for SchedulerPopen
import subprocess
import multiprocessing
import time

from typing import Callable, Iterable, Union, Optional

import astunparse

try:
    import pythran
except ImportError:
    pythran = False

try:
    from IPython.core.getipython import get_ipython
except ImportError:
    pass

path_root = Path.home() / ".fluidpythran"
ext_suffix = sysconfig.get_config_var("EXT_SUFFIX") or ".so"

# if pythran and pythran.__version__ <= "0.9.0":

# avoid a Pythran bug with -o option
# it is bad because then we do not support using many Python versions

ext_suffix_short = "." + ext_suffix.rsplit(".", 1)[-1]


def get_module_name(frame):
    """Get the full module name"""
    module = inspect.getmodule(frame[0])
    if module is not None:
        module_name = module.__name__
        if module_name in ("__main__", "<run_path>"):
            module_name = inspect.getmodulename(frame.filename)
    else:
        module_name = inspect.getmodulename(frame.filename)

    if module_name is None:
        # ipython ?
        src, module_name = get_info_from_ipython()

    return module_name


def modification_date(filename):
    """Get the modification date of a file"""
    return datetime.fromtimestamp(os.path.getmtime(filename))


def has_to_build(output_file: Path, input_file: Path):
    """Check if a file has to be (re)built"""
    output_file = Path(output_file)
    if not output_file.exists():
        return True
    mod_date_output = modification_date(output_file)
    if mod_date_output < modification_date(input_file):
        return True
    return False


def get_source_without_decorator(func: Callable):
    """Get the source of a function without its decorator"""
    src = inspect.getsource(func)
    return strip_typehints(re.sub(r"@.*?\sdef\s", "def ", src))


class TypeHintRemover(ast.NodeTransformer):
    """Strip the type hints

    from https://stackoverflow.com/a/42734810/1779806
    """

    def visit_FunctionDef(self, node):
        # remove the return type defintion
        node.returns = None
        # remove all argument annotations
        if node.args.args:
            for arg in node.args.args:
                arg.annotation = None
        return node


def strip_typehints(source):
    """Strip the type hints from a function"""
    # parse the source code into an AST
    parsed_source = ast.parse(source)
    # remove all type annotations, function return type definitions
    # and import statements from 'typing'
    transformed = TypeHintRemover().visit(parsed_source)
    # convert the AST back to source code
    return astunparse.unparse(transformed)


def make_hex(src):
    """Produce a hash from a sting"""
    return hashlib.md5(src.encode("utf8")).hexdigest()


def get_ipython_input(last=True):
    """Get the input code when called from IPython"""
    ip = get_ipython()

    hist_raw = ip.history_manager.input_hist_raw
    if last:
        return hist_raw[-1]
    else:
        return "\n".join(hist_raw)


def get_info_from_ipython():
    """Get the input code and a "filename" when called from IPython"""
    src = get_ipython_input()
    hex_input = make_hex(src)
    dummy_filename = "__ipython__" + hex_input
    return src, dummy_filename


class SchedulerPopen:
    """Limit the number of Pythran compilations performed in parallel

    """

    deltat = 0.2

    def __init__(self, parallel=True):
        self.processes = []
        if parallel:
            self.nb_cpus = multiprocessing.cpu_count()
        else:
            self.nb_cpus = 1

    def launch_popen(self, words_command, cwd=None, parallel=True):
        """Launch a program (blocking if too many processes launched)"""

        if parallel:
            limit = self.nb_cpus
        else:
            limit = 1

        while len(self.processes) >= limit:
            time.sleep(self.deltat)
            self.processes = [
                process for process in self.processes if process.poll() is None
            ]

        process = subprocess.Popen(words_command, cwd=cwd)
        self.processes.append(process)
        return process


scheduler = SchedulerPopen()


def name_ext_from_path_pythran(path_pythran):

    if path_pythran.exists():
        with open(path_pythran) as file:
            src = file.read()
    else:
        src = ""

    return path_pythran.stem + "_" + make_hex(src) + ext_suffix_short


def compile_pythran_files(
    paths: Iterable[Path], str_pythran_flags: str, parallel=True
):

    pythran_flags = str_pythran_flags.strip().split()

    for path in paths:
        name_ext = name_ext_from_path_pythran(path)
        words_command = ["pythran", path.name, "-o", name_ext]
        words_command.extend(pythran_flags)
        print("pythranize file", path)
        scheduler.launch_popen(
            words_command, cwd=str(path.parent), parallel=parallel
        )


def compile_pythran_file(
    path: Union[Path, str],
    name_ext_file: Optional[str] = None,
    native=True,
    xsimd=True,
    openmp=False,
):

    if not isinstance(path, Path):
        path = Path(path)

    words_command = ["pythran", "-v", str(path)]

    if name_ext_file is not None:
        words_command.extend(("-o", name_ext_file))

    if native:
        words_command.append("-march=native")

    if xsimd:
        words_command.append("-DUSE_XSIMD")

    if openmp:
        words_command.append("-fopenmp")

    # return the process
    return scheduler.launch_popen(words_command, cwd=str(path.parent))


def has_to_pythranize_at_import():
    """Check if fluidpythran has to pythranize at import time"""
    return "PYTHRANIZE_AT_IMPORT" in os.environ


def import_from_path(path: Path, module_name: str):
    """Import a .py file or an extension from its path

    """
    if not path.exists():
        raise ImportError(
            f"File {path} does not exist. "
            f"[path.name for path in path.parent.glob('*')]:\n{[path.name for path in path.parent.glob('*')]}\n"
        )

    if module_name in sys.modules:
        module = sys.modules[module_name]
        if module.__file__.endswith(ext_suffix_short) and Path(module.__file__) == path:
            return module

    if "." in module_name:
        package_name, mod_name = module_name.rsplit(".", 1)
        name_file = path.name.split(".", 1)[0]
        if mod_name != name_file:
            module_name = ".".join((package_name, name_file))
    else:
        module_name = path.stem

    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
