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

import re
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


from transonic.analyses import extast
from transonic.analyses.justintime import analysis_jit
from transonic.annotation import (
    make_signatures_from_typehinted_func,
    normalize_type_name,
)
from transonic.aheadoftime import TransonicTemporaryJITMethod
from transonic.backends import backends
from transonic.compiler import compile_extension, ext_suffix
from transonic.config import has_to_replace, backend_default
from transonic.log import logger
from transonic import mpi
from transonic.util import (
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
    write_if_has_to_write,
)


modules = {}

path_jit = mpi.Path(path_root) / backend_default / "__jit__"


if mpi.rank == 0:
    path_jit.mkdir(parents=True, exist_ok=True)
mpi.barrier()

_COMPILE_JIT = strtobool(os.environ.get("TRANSONIC_COMPILE_JIT", "True"))


def set_compile_jit(value):
    global _COMPILE_JIT
    _COMPILE_JIT = value


class ModuleJIT:
    """Representation of a module using jit"""

    def __init__(self, backend, frame=None):

        self.backend = backend
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

        source = self.get_source()
        self.jitted_dicts, self.codes_dependance, self.codes_dependance_classes, self.code_ext, self.special = analysis_jit(
            source, self.filename
        )
        # Write exterior code for functions
        for file_name, code in self.code_ext["function"].items():
            path_ext = path_jit / self.module_name.replace(".", os.path.sep)
            path_ext_file = path_ext / (file_name + ".py")
            write_if_has_to_write(path_ext_file, code, logger.info)

        # Write exterior code for classes
        for file_name, code in self.code_ext["classe"].items():
            path_ext = (
                path_jit.parent
                / "__jit_classes__"
                / self.module_name.replace(".", os.path.sep)
            )
            path_ext_file = path_ext / (file_name + ".py")
            write_if_has_to_write(path_ext_file, code, logger.info)

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


def _get_module_jit(backend="pythran", index_frame: int = 2):
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
        return ModuleJIT(backend=backend, frame=frame)


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


def jit(func=None, backend="pythran", native=False, xsimd=False, openmp=False):
    """Decorator to record that the function has to be jit compiled

    """
    decor = JIT(backend=backend, native=native, xsimd=xsimd, openmp=openmp)
    if callable(func):
        decor._decorator_no_arg = True
        return decor(func)
    else:
        return decor


class JIT:
    """Decorator used internally by the public jit decorator
    """

    def __init__(self, backend, native=False, xsimd=False, openmp=False):
        self.backend = backend
        self.native = native
        self.xsimd = xsimd
        self.openmp = openmp
        self._decorator_no_arg = False

        self.backend_func = None
        self.compiling = False
        self.process = None

    def __call__(self, func, backend=backend_default):

        if isinstance(backend, str):
            backend = backends[backend_default]

        if not has_to_replace:
            return func

        if is_method(func):
            return TransonicTemporaryJITMethod(
                func, self.native, self.xsimd, self.openmp
            )

        if not pythran:
            return func

        func_name = func.__name__

        if self._decorator_no_arg:
            index_frame = 3
        else:
            index_frame = 2

        mod = _get_module_jit(self.backend, index_frame)
        mod.jit_functions[func_name] = self
        module_name = mod.module_name

        path_backend = path_jit / module_name.replace(".", os.path.sep)

        if mpi.rank == 0:
            path_backend.mkdir(parents=True, exist_ok=True)
        mpi.barrier()

        if backend_default == "pythran":
            suffix = ".pythran"
        else:
            suffix = ".pxd"

        path_backend = (path_backend / func_name).with_suffix(".py")
        path_backend_header = path_backend.with_suffix(suffix)

        if path_backend.exists():
            if not mod.is_dummy_file and has_to_build(path_backend, mod.filename):
                has_to_write = True
            else:
                has_to_write = False
        else:
            has_to_write = True

        src = None

        if has_to_write:
            src = mod.codes_dependance[func_name]
            if func_name in mod.special:
                if func_name in mod.jitted_dicts["functions"]:
                    src += extast.unparse(
                        mod.jitted_dicts["functions"][func_name]
                    )
                elif func_name in mod.jitted_dicts["methods"]:
                    src += extast.unparse(mod.jitted_dicts["methods"][func_name])
            else:
                # TODO find a prettier solution to remove decorator for cython
                # than doing two times a regex
                src += re.sub(
                    r"@.*?\sdef\s", "def ", get_source_without_decorator(func)
                )
            if path_backend.exists() and mpi.rank == 0:
                with open(path_backend) as file:
                    src_old = file.read()
                if src_old == src:
                    has_to_write = False

            if has_to_write and mpi.rank == 0:
                logger.debug(f"write code in file {path_backend}")
                with open(path_backend, "w") as file:
                    file.write(src)
                    file.flush()

        if src is None and mpi.rank == 0:
            with open(path_backend) as file:
                src = file.read()

        hex_src = None
        name_mod = None
        if mpi.rank == 0:
            # hash from src (to produce the extension name)
            hex_src = make_hex(src)
            name_mod = ".".join(
                path_backend.absolute()
                .relative_to(path_root)
                .with_suffix("")
                .parts
            )

        hex_src = mpi.bcast(hex_src)
        name_mod = mpi.bcast(name_mod)

        def backenize_with_new_header(arg_types="no types"):

            if backend_default == "pythran":
                keyword = "export "
            elif backend_default == "cython":
                keyword = "cdef "

            # Include signature comming from type hints
            signatures = make_signatures_from_typehinted_func(func)
            exports = set(keyword + signature for signature in signatures)

            if arg_types != "no types":
                export_new = "{}{}({})".format(
                    keyword, func_name, ", ".join(arg_types)
                )
                if export_new not in exports:
                    exports.add(export_new)

            if not exports:
                return

            try:
                path_backend_header_exists = path_backend_header.exists()
            except TimeoutError:
                raise RuntimeError(
                    f"A MPI communication in Transonic failed when compiling "
                    f"function {func}. This usually arises when a jitted "
                    "function has to be compiled in MPI and is only called "
                    f"by one process (rank={mpi.rank})."
                )

            if path_backend_header_exists:
                # get the old signature(s)

                exports_old = None
                if mpi.rank == 0:
                    with open(path_backend_header) as file:
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
                    f"write {backend_default} signature in file {path_backend_header} with types\n{arg_types}"
                )
                with open(path_backend_header, "w") as file:
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
            self.path_extension = path_backend.with_name(name_ext_file)

            self.compiling = True

            self.process = compile_extension(
                path_backend,
                backend_default,
                name_ext_file,
                native=self.native,
                xsimd=self.xsimd,
                openmp=self.openmp,
            )

        ext_files = None
        if mpi.rank == 0:
            glob_name_ext_file = func_name + "_" + hex_src + "_*" + ext_suffix
            ext_files = list(
                mpi.PathSeq(path_backend).parent.glob(glob_name_ext_file)
            )
        ext_files = mpi.bcast(ext_files)

        if not ext_files:
            if has_to_compile_at_import() and _COMPILE_JIT:
                backenize_with_new_header()
            self.backend_func = None
        else:
            path_ext = max(ext_files, key=lambda p: p.stat().st_ctime)
            backend_module = import_from_path(path_ext, name_mod)
            self.backend_func = getattr(backend_module, func_name)

        @wraps(func)
        def type_collector(*args, **kwargs):

            if self.compiling:
                if not self.process.is_alive():
                    self.compiling = False
                    time.sleep(0.1)
                    backend_module = import_from_path(
                        self.path_extension, name_mod
                    )
                    assert backend.check_if_compiled(backend_module)
                    self.backend_func = getattr(backend_module, func_name)

            error = False
            try:
                return self.backend_func(*args, **kwargs)
            except TypeError as err:
                # need to compiled or recompile
                if self.backend_func:
                    error = str(err)
                    if (
                        error.startswith("Invalid call to pythranized function `")
                        and " (reshaped)" in error
                    ):
                        logger.error(
                            "It seems that a jitted Pythran function has been called "
                            'with a "reshaped" array which is not supported by Pythran.'
                        )
                        raise

            if self.compiling or not _COMPILE_JIT:
                return func(*args, **kwargs)

            if (
                self.backend_func
                and error
                and error.startswith("Invalid call to pythranized function `")
            ):
                logger.debug(error)
                logger.info(
                    f"Pythran function `{func_name}` called with new types."
                )
                logger.debug(
                    "Transonic is going to recompute the function for the new types."
                )

            arg_types = [
                make_pythran_type_name(arg)
                for arg in itertools.chain(args, kwargs.values())
            ]

            backenize_with_new_header(arg_types)
            return func(*args, **kwargs)

        return type_collector
