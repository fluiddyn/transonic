"""Cached JIT compilation
=========================

User API
--------

.. autofunction:: jit

.. autofunction:: set_compile_jit

Internal API
------------

.. autoclass:: ModuleJIT
   :members:
   :private-members:

.. autofunction:: _get_module_jit

.. autoclass:: JIT
   :members:
   :private-members:

.. autofunction:: make_pythran_type_name

Notes
-----

Serge talked about @jit (see https://gist.github.com/serge-sans-paille/28c86d2b33cd561ba5e50081716b2cf4)

It's indeed a good idea!

With "# transonic import" and @include the implementation isn't
too complicated.

- At import time, we create one .py file per jit function.

- At run time, we create (and complete when needed) a corresponding
  .pythran file with signature(s).

  The jit decorator:

  * at the first call, get the types, create the .pythran file and call
    Pythran.

  * then, try to call the pythran function and if it fails with
    a Pythran TypeError, correct the .pythran file and recompile.

Note: During the compilation (the "warmup" of the JIT), the Python function is
used.

"""

import inspect
import itertools
import os
import sys
import time
from distutils.util import strtobool
from functools import wraps

try:
    import numpy as np
except ImportError:
    np = None

from .pythranizer import compile_extension, ext_suffix

from .util import (
    get_module_name,
    has_to_build,
    get_source_without_decorator,
    path_root,
    get_info_from_ipython,
    make_hex,
    has_to_compile_at_import,
    import_from_path,
    pythran,
    is_method,
)
from .annotation import make_signatures_from_typehinted_func, normalize_type_name

from .aheadoftime import TransonicTemporaryJITMethod

from .compat import open
from . import mpi
from .log import logger
from .config import has_to_replace

modules = {}


path_jit = mpi.Path(path_root) / "__jit__"
if mpi.rank == 0:
    path_jit.mkdir(parents=True, exist_ok=True)
mpi.barrier()

_COMPILE_JIT = strtobool(os.environ.get("TRANSONIC_COMPILE_JIT", "True"))


def set_compile_jit(value):
    global _COMPILE_JIT
    _COMPILE_JIT = value


class ModuleJIT:
    """Representation of a module using jit"""

    def __init__(self, frame=None):

        if frame is None:
            frame = inspect.stack()[1]

        self.filename = frame.filename
        if self.filename.startswith("<ipython-"):
            self.is_dummy_file = True
            self._ipython_src, self.filename = get_info_from_ipython()
            self.module_name = self.filename
        else:
            self.is_dummy_file = False
            self.module_name = get_module_name(frame)
        modules[self.module_name] = self
        self.used_functions = {}
        self.jit_functions = {}

    def record_used_function(self, func, names):
        if isinstance(names, str):
            names = (names,)

        for name in names:
            if name in self.used_functions:
                self.used_functions[name].append(func)
            else:
                self.used_functions[name] = [func]

    def get_source(self):
        if self.is_dummy_file:
            return self._ipython_src
        try:
            mod = sys.modules[self.module_name]
        except KeyError:
            with open(self.filename) as file:
                return file.read()
        else:
            return inspect.getsource(mod)


def _get_module_jit(index_frame: int = 2):
    """Get the ModuleJIT instance corresponding to the calling module

    Parameters
    ----------

    index_frame : int

      Index (in :code:`inspect.stack()`) of the frame to be selected

    """
    try:
        frame = inspect.stack()[index_frame]
    except IndexError:
        logger.error(
            f"index_frame {index_frame}"
            f"{[frame[1] for frame in inspect.stack()]}"
        )
        raise

    module_name = get_module_name(frame)

    if module_name in modules:
        return modules[module_name]
    else:
        return ModuleJIT(frame=frame)


def make_pythran_type_name(obj: object):
    """return the Pythran type name"""
    name = type(obj).__name__
    name = normalize_type_name(name)

    if np and isinstance(obj, np.ndarray):
        name = obj.dtype.name
        if obj.ndim != 0:
            name += "[" + ", ".join([":"] * obj.ndim) + "]"

    if name in ("list", "set", "dict"):
        if not obj:
            raise ValueError(
                f"cannot determine the Pythran type from an empty {name}"
            )

    if name in ("list", "set"):
        item_type = type(obj[0])
        # FIXME: we could check if the iterable is homogeneous...
        name = item_type.__name__ + " " + name

    if name == "dict":
        for key, value in obj.items():
            break
        # FIXME: we could check if the dict is homogeneous...
        name = type(key).__name__ + ": " + type(value).__name__ + " dict"

    return name


def jit(func=None, native=True, xsimd=True, openmp=False):
    """Decorator to record that the function has to be jit compiled

    """
    decor = JIT(native=native, xsimd=xsimd, openmp=openmp)
    if callable(func):
        decor._decorator_no_arg = True
        return decor(func)
    else:
        return decor


class JIT:
    """Decorator used internally by the public jit decorator
    """

    def __init__(self, native=True, xsimd=True, openmp=False):
        self.native = native
        self.xsimd = xsimd
        self.openmp = openmp
        self._decorator_no_arg = False

        self.pythran_func = None
        self.compiling = False
        self.process = None

    def __call__(self, func):

        if is_method(func):
            return TransonicTemporaryJITMethod(
                func, self.native, self.xsimd, self.openmp
            )

        if not pythran or not has_to_replace:
            return func

        func_name = func.__name__

        if self._decorator_no_arg:
            index_frame = 3
        else:
            index_frame = 2

        mod = _get_module_jit(index_frame)
        mod.jit_functions[func_name] = self
        module_name = mod.module_name

        path_pythran = path_jit / module_name.replace(".", os.path.sep)

        if mpi.rank == 0:
            path_pythran.mkdir(parents=True, exist_ok=True)
        mpi.barrier()

        path_pythran = (path_pythran / func_name).with_suffix(".py")
        path_pythran_header = path_pythran.with_suffix(".pythran")

        if path_pythran.exists():
            if not mod.is_dummy_file and has_to_build(path_pythran, mod.filename):
                has_to_write = True
            else:
                has_to_write = False
        else:
            has_to_write = True

        src = None

        if has_to_write:
            import_lines = [
                line.split("# transonic ")[1]
                for line in mod.get_source().split("\n")
                if line.startswith("# transonic ") and "import" in line
            ]
            src = "\n".join(import_lines) + "\n\n"

            src += get_source_without_decorator(func)

            if func_name in mod.used_functions:
                functions = mod.used_functions[func_name]
                for function in functions:
                    src += "\n" + get_source_without_decorator(function)

            if path_pythran.exists() and mpi.rank == 0:
                with open(path_pythran) as file:
                    src_old = file.read()
                if src_old == src:
                    has_to_write = False

            if has_to_write and mpi.rank == 0:
                logger.debug(f"write code in file {path_pythran}")
                with open(path_pythran, "w") as file:
                    file.write(src)
                    file.flush()

        if src is None and mpi.rank == 0:
            with open(path_pythran) as file:
                src = file.read()

        hex_src = None
        name_mod = None
        if mpi.rank == 0:
            # hash from src (to produce the extension name)
            hex_src = make_hex(src)
            name_mod = ".".join(
                path_pythran.absolute()
                .relative_to(path_root)
                .with_suffix("")
                .parts
            )

        hex_src = mpi.bcast(hex_src)
        name_mod = mpi.bcast(name_mod)

        def pythranize_with_new_header(arg_types="no types"):

            # Include signature comming from type hints
            signatures = make_signatures_from_typehinted_func(func)
            exports = set("export " + signature for signature in signatures)

            if arg_types != "no types":
                export_new = "export {}({})".format(
                    func_name, ", ".join(arg_types)
                )
                if export_new not in exports:
                    exports.add(export_new)

            if not exports:
                return

            try:
                path_pythran_header_exists = path_pythran_header.exists()
            except TimeoutError:
                raise RuntimeError(
                    f"A MPI communication in Transonic failed when compiling "
                    f"function {func}. This usually arises when a jitted "
                    "function has to be compiled in MPI and is only called "
                    f"by one process (rank={mpi.rank})."
                )

            if path_pythran_header_exists:
                # get the old signature(s)

                exports_old = None
                if mpi.rank == 0:
                    with open(path_pythran_header) as file:
                        exports_old = [
                            export.strip() for export in file.readlines()
                        ]
                exports_old = mpi.bcast(exports_old)

                # FIXME: what do we do with the old signatures?
                exports.update(exports_old)

            header = "\n".join(sorted(exports)) + "\n"

            mpi.barrier()
            if mpi.rank == 0:
                logger.debug(
                    f"write Pythran signature in file {path_pythran_header} with types\n{arg_types}"
                )
                with open(path_pythran_header, "w") as file:
                    file.write(header)
                    file.flush()

            # compute the new path of the extension
            hex_header = make_hex(header)
            # if mpi.nb_proc > 1:
            #     hex_header0 = mpi.bcast(hex_header)
            #     assert hex_header0 == hex_header
            name_ext_file = (
                func_name + "_" + hex_src + "_" + hex_header + ext_suffix
            )
            self.path_extension = path_pythran.with_name(name_ext_file)

            self.compiling = True

            self.process = compile_extension(
                path_pythran,
                name_ext_file,
                native=self.native,
                xsimd=self.xsimd,
                openmp=self.openmp,
            )

        ext_files = None
        if mpi.rank == 0:
            glob_name_ext_file = func_name + "_" + hex_src + "_*" + ext_suffix
            ext_files = list(
                mpi.PathSeq(path_pythran).parent.glob(glob_name_ext_file)
            )
        ext_files = mpi.bcast(ext_files)

        if not ext_files:
            if has_to_compile_at_import() and _COMPILE_JIT:
                pythranize_with_new_header()
            self.pythran_func = None
        else:
            path_ext = max(ext_files, key=lambda p: p.stat().st_ctime)
            module_pythran = import_from_path(path_ext, name_mod)
            self.pythran_func = getattr(module_pythran, func_name)

        @wraps(func)
        def type_collector(*args, **kwargs):

            if self.compiling:
                if not self.process.is_alive():
                    self.compiling = False
                    time.sleep(0.1)
                    module_pythran = import_from_path(
                        self.path_extension, name_mod
                    )
                    assert hasattr(module_pythran, "__pythran__")
                    self.pythran_func = getattr(module_pythran, func_name)

            try:
                return self.pythran_func(*args, **kwargs)
            except TypeError:
                # need to compiled or recompile
                pass

            if self.compiling or not _COMPILE_JIT:
                return func(*args, **kwargs)

            arg_types = [
                make_pythran_type_name(arg)
                for arg in itertools.chain(args, kwargs.values())
            ]

            pythranize_with_new_header(arg_types)

            return func(*args, **kwargs)

        return type_collector
