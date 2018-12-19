"""Internal utilities
=====================

Public API
----------

.. autofunction:: set_pythranize_at_import

Internal API
------------

.. autofunction:: find_module_name_from_path

.. autofunction:: get_module_name

.. autofunction:: modification_date

.. autofunction:: has_to_build

.. autofunction:: get_source_without_decorator

.. autoclass:: TypeHintRemover
   :members:
   :private-members:

.. autofunction:: strip_typehints

.. autofunction:: get_ipython_input

.. autofunction:: get_info_from_ipython

.. autofunction:: has_to_pythranize_at_import

.. autofunction:: import_from_path

.. autofunction:: query_yes_no

.. autofunction:: clear_cached_extensions

.. autofunction:: is_method
"""

import os
import sys
import inspect
import re
from pathlib import Path
import ast
import importlib.util
from distutils.util import strtobool
import shutil

from typing import Callable

import astunparse

try:
    import black
except ImportError:
    black = False

try:
    import pythran
except ImportError:
    pythran = False

try:
    from IPython.core.getipython import get_ipython
except ImportError:
    pass

from .pythranizer import (
    ext_suffix,
    name_ext_from_path_pythran,
    make_hex,
    modification_date,
    has_to_build,
)

from .config import path_root

__all__ = ["modification_date", "has_to_build"]


path_cachedjit_classes = path_root / "__cachedjit_classes__"


def find_module_name_from_path(path_py: Path):
    """Find the module name from the path of a Python file

    It is done by looking to ``sys.path`` to see how the module can be imported.

    """

    cwd = Path.cwd()
    path = path_py.absolute().parent
    module_name = path_py.stem

    # special case for cachedjit_classes
    try:
        path_rel = path.relative_to(path_cachedjit_classes)
    except ValueError:
        pass
    else:
        tmp = [path_cachedjit_classes.name]
        name_pack = str(path_rel).replace(os.path.sep, ".")
        if name_pack:
            tmp.append(name_pack)
        tmp.append(module_name)
        return ".".join(tmp)

    while path.parents:
        if path == cwd or str(path) in sys.path:
            return module_name

        module_name = path.name + "." + module_name
        path = path.parent

    return path_py.stem


def get_module_name(frame):
    """Get the full module name"""
    module = inspect.getmodule(frame[0])
    filename = None
    if module is not None:
        module_name = module.__name__
        if module_name in ("__main__", "<run_path>"):
            filename = frame.filename
    else:
        filename = frame.filename

    if filename is not None:
        module_name = find_module_name_from_path(Path(filename))

    if module_name is None:
        # ipython ?
        src, module_name = get_info_from_ipython()

    return module_name


def get_source_without_decorator(func: Callable):
    """Get the source of a function without its decorator"""
    src = inspect.getsource(func)

    # de-indent the code
    nb_spaces = 0
    for c in src:
        if not c.isspace():
            break
        nb_spaces += 1

    if nb_spaces > 0:
        lines = [line[nb_spaces:] for line in src.split("\n")]
        src = "\n".join(lines)

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

    if black:
        source = black.format_str(source, line_length=82)

    # parse the source code into an AST
    parsed_source = ast.parse(source)
    # remove all type annotations, function return type definitions
    # and import statements from 'typing'
    transformed = TypeHintRemover().visit(parsed_source)
    # convert the AST back to source code
    striped_code = astunparse.unparse(transformed)

    # bad hack to conserve the comments...
    sep = ":(\n)+    "
    head = re.split(sep, striped_code, maxsplit=1)[0]
    body = re.split(sep, source, maxsplit=1)[-1]
    return head + ":\n    " + body


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


_PYTHRANIZE_AT_IMPORT = None


def set_pythranize_at_import(value=True):
    """Control the "pythranize_at_import" mode"""
    global _PYTHRANIZE_AT_IMPORT
    _PYTHRANIZE_AT_IMPORT = value


def has_to_pythranize_at_import():
    """Check if fluidpythran has to pythranize at import time"""
    if _PYTHRANIZE_AT_IMPORT is not None:
        return _PYTHRANIZE_AT_IMPORT
    return "PYTHRANIZE_AT_IMPORT" in os.environ


def import_from_path(path: Path, module_name: str):
    """Import a .py file or an extension from its path

    """
    if not path.exists():
        raise ImportError(
            f"File {path} does not exist. "
            f"[path.name for path in path.parent.glob('*')]:\n{[path.name for path in path.parent.glob('*')]}\n"
        )

    if "." in module_name:
        package_name, mod_name = module_name.rsplit(".", 1)
        name_file = path.name.split(".", 1)[0]
        if mod_name != name_file:
            module_name = ".".join((package_name, name_file))
    else:
        module_name = path.stem

    if module_name in sys.modules:
        module = sys.modules[module_name]

        if module.__file__.endswith(ext_suffix) and Path(module.__file__) == path:
            return module

    spec = importlib.util.spec_from_file_location(module_name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def query_yes_no(question: str, default: str = None, force: bool = False):
    """User yes or no query"""
    if force:
        return True

    if default is None:
        end = "(y/n)"
        default = ""
    elif default == "y":
        end = "([y]/n)"
    elif default == "n":
        end = "(y/[n])"

    print(f"{question} {end}")
    while True:
        answer = input()
        if answer == "":
            answer = default
        try:
            return strtobool(answer)
        except ValueError:
            print('Please respond with "y" or "n".')


def clear_cached_extensions(module_name: str, force: bool = False):
    """Delete the cached extensions related to a module

    """

    from .justintime import path_cachedjit

    if module_name.endswith(".py"):
        module_name = module_name[:-3]

    if os.path.sep not in module_name:
        relative_path = module_name.replace(".", os.path.sep)
    else:
        relative_path = module_name

    path_pythran_dir_jit = path_cachedjit / relative_path

    relative_path = Path(relative_path)

    path_pythran = relative_path.parent / (
        "__pythran__/" + relative_path.name + ".py"
    )
    path_ext = path_pythran.with_name(name_ext_from_path_pythran(path_pythran))

    if not path_pythran_dir_jit.exists() and not (
        path_pythran.exists() or path_ext.exists()
    ):
        print(
            f"Not able to find cached extensions corresponding to {module_name}"
        )
        print("Nothing to do! ✨ 🍰 ✨.")
        return

    if path_pythran_dir_jit.exists() and query_yes_no(
        f"Do you confirm that you want to delete the cached files for {module_name}",
        default="y",
        force=force,
    ):
        print(f"Remove directory {path_pythran_dir_jit}")
        shutil.rmtree(str(path_pythran_dir_jit))

    if path_pythran.exists() or path_ext.exists():
        if query_yes_no(
            f"Do you confirm that you want to delete the AOT cache for {module_name}",
            default="y",
            force=force,
        ):
            for path in (path_pythran, path_ext):
                if path.exists():
                    path.unlink()


def is_method(func):
    """Determine wether a function is going to be used as a method"""
    signature = inspect.signature(func)
    try:
        answer = next(iter(signature.parameters.keys())) == "self"
    except StopIteration:
        answer = False

    return answer
