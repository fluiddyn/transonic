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

"""

import os
import inspect
from datetime import datetime
import re
from pathlib import Path
import ast
import hashlib
import sysconfig

# for SchedulerPopen
import subprocess
import multiprocessing
import time

from typing import Callable

import astunparse

try:
    from IPython.core.getipython import get_ipython
except ImportError:
    pass

path_root = Path.home() / ".fluidpythran"
ext_suffix = sysconfig.get_config_var("EXT_SUFFIX") or ".so"


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

    def launch_popen(self, words_command, cwd=None):
        """Launch a program (blocking if too many processes launched)"""
        while len(self.processes) >= self.nb_cpus:
            time.sleep(self.deltat)
            self.processes = [
                process for process in self.processes if process.poll() is None
            ]

        process = subprocess.Popen(words_command, cwd=cwd)
        self.processes.append(process)
        return process


def compile_pythran_files(paths, str_pythran_flags, parallel=True):

    pythran_flags = str_pythran_flags.strip().split()
    scheduler = SchedulerPopen()

    for path in paths:
        words_command = ["pythran", path.name]
        words_command.extend(pythran_flags)
        print("pythranize file", path)
        scheduler.launch_popen(words_command, cwd=str(path.parent))
