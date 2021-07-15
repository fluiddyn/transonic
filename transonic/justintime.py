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

import inspect
import itertools
import os
import sys
import time
from functools import wraps

from transonic.analyses.justintime import analysis_jit
from transonic.aheadoftime import TransonicTemporaryJITMethod
from transonic.backends import backends, get_backend_name_module
from transonic.config import has_to_replace, backend_default
from transonic.log import logger
from transonic import mpi
from transonic.util import (
    get_module_name,
    has_to_build,
    path_root,
    get_info_from_ipython,
    make_hex,
    has_to_compile_at_import,
    import_from_path,
    is_method,
    write_if_has_to_write,
    can_import_accelerator,
    format_str,
    strtobool,
)

modules_backends = {backend_name: {} for backend_name in backends.keys()}
modules = modules_backends[backend_default]

_COMPILE_JIT = strtobool(os.environ.get("TRANSONIC_COMPILE_JIT", "True"))


def set_compile_jit(value):
    global _COMPILE_JIT
    _COMPILE_JIT = value


class ModuleJIT:
    """Representation of a module using jit"""

    def __init__(self, backend_name: str, frame=None):

        self.backend_name = backend_name
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
        modules_backends[backend_name][self.module_name] = self
        self.used_functions = {}
        self.jit_functions = {}

        (
            jitted_dicts,
            codes_dependance,
            codes_dependance_classes,
            code_ext,
            special,
        ) = analysis_jit(self.get_source(), self.filename, backend_name)

        self.info_analysis = {
            "jitted_dicts": jitted_dicts,
            "codes_dependance": codes_dependance,
            "codes_dependance_classes": codes_dependance_classes,
            "special": special,
        }

        self.backend = backend = backends[backend_name]
        path_jit = mpi.Path(backend.jit.path_base)
        path_jit_class = mpi.Path(backend.jit.path_class)

        # TODO: check if these files have to be written here...
        # Write exterior code for functions
        for file_name, code in code_ext["function"].items():
            path_ext = path_jit / self.module_name.replace(".", os.path.sep)
            path_ext_file = path_ext / (file_name + ".py")
            write_if_has_to_write(path_ext_file, format_str(code), logger.info)

        # Write exterior code for classes
        for file_name, code in code_ext["class"].items():
            path_ext = path_jit_class / self.module_name.replace(".", os.path.sep)
            path_ext_file = path_ext / (file_name + ".py")
            write_if_has_to_write(path_ext_file, format_str(code), logger.info)

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


def _get_module_jit(backend_name: str = None, index_frame: int = 2, frame=None):
    """Get the ModuleJIT instance corresponding to the calling module

    Parameters
    ----------

    index_frame : int

      Index (in :code:`inspect.stack()`) of the frame to be selected

    """

    if frame is None:
        try:
            frame = inspect.stack()[index_frame]
        except IndexError:
            logger.error(
                f"index_frame {index_frame}"
                f"{[frame[1] for frame in inspect.stack()]}"
            )
            raise

    module_name = get_module_name(frame)

    if backend_name is None:
        backend_name = get_backend_name_module(module_name)

    modules = modules_backends[backend_name]

    if module_name in modules:
        return modules[module_name]
    else:
        return ModuleJIT(backend_name=backend_name, frame=frame)


def jit(func=None, backend: str = None, native=False, xsimd=False, openmp=False):
    """Decorator to record that the function has to be jit compiled

    """
    frame = inspect.stack()[1]
    decor = JIT(frame, backend=backend, native=native, xsimd=xsimd, openmp=openmp)
    if callable(func):
        return decor(func)
    else:
        return decor


class JIT:
    """Decorator used internally by the public jit decorator
    """

    def __init__(
        self, frame, backend: str, native=False, xsimd=False, openmp=False
    ):

        self.mod = _get_module_jit(backend, frame=frame)

        self.backend = self.mod.backend
        self.native = native
        self.xsimd = xsimd
        self.openmp = openmp
        self._decorator_no_arg = False

        self.backend_func = None
        self.compiling = False
        self.process = None

    def __call__(self, func):
        if not has_to_replace:
            return func

        if is_method(func):
            return TransonicTemporaryJITMethod(
                func, self.native, self.xsimd, self.openmp
            )

        if not can_import_accelerator(self.backend.name):
            logger.warning(
                "Cannot accelerate a jitted function because "
                f"{self.backend.name_capitalized} is not importable."
            )
            return func

        func_name = func.__name__

        backend = self.backend
        mod = self.mod
        mod.jit_functions[func_name] = self
        module_name = mod.module_name

        path_jit = mpi.Path(backend.jit.path_base)
        path_backend = path_jit / module_name.replace(".", os.path.sep)

        if mpi.rank == 0:
            path_backend.mkdir(parents=True, exist_ok=True)
        mpi.barrier()

        path_backend = (path_backend / func_name).with_suffix(".py")
        if backend.suffix_header:
            path_backend_header = path_backend.with_suffix(backend.suffix_header)
        else:
            path_backend_header = False

        if path_backend.exists():
            if not mod.is_dummy_file and has_to_build(path_backend, mod.filename):
                has_to_write = True
            else:
                has_to_write = False
        else:
            has_to_write = True

        src = None

        if has_to_write:
            src, has_to_write = backend.jit.make_backend_source(
                mod.info_analysis, func, path_backend
            )

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

            header_object = backend.jit.make_new_header(func, arg_types)

            header_code = backend.jit.merge_old_and_new_header(
                path_backend_header, header_object, func
            )
            backend.jit.write_new_header(
                path_backend_header, header_code, arg_types
            )

            # compute the new path of the extension
            hex_header = make_hex(header_code)
            # if mpi.nb_proc > 1:
            #     hex_header0 = mpi.bcast(hex_header)
            #     assert hex_header0 == hex_header
            name_ext_file = (
                func_name
                + "_"
                + hex_src
                + "_"
                + hex_header
                + backend.suffix_extension
            )
            self.path_extension = path_backend.with_name(name_ext_file)

            self.compiling, self.process = backend.compile_extension(
                path_backend,
                name_ext_file,
                native=self.native,
                xsimd=self.xsimd,
                openmp=self.openmp,
            )

            # for backend like numba
            if not self.compiling:
                backend_module = import_from_path(self.path_extension, name_mod)
                assert backend.check_if_compiled(backend_module)
                self.backend_func = getattr(backend_module, func_name)

        ext_files = None
        if mpi.rank == 0:
            glob_name_ext_file = (
                func_name + "_" + hex_src + "_*" + backend.suffix_extension
            )
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

        # this is the function that will be called by the user
        @wraps(func)
        def type_collector(*args, **kwargs):

            if self.compiling:
                if not self.process.is_alive(raise_if_error=True):
                    self.compiling = False
                    time.sleep(0.1)
                    backend_module = import_from_path(
                        self.path_extension, name_mod
                    )
                    assert backend.check_if_compiled(backend_module)
                    self.backend_func = getattr(backend_module, func_name)

            try:
                return self.backend_func(*args, **kwargs)
            except TypeError as err:
                # need to compiled or recompile
                error = False
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
                    logger.debug(error)

            if self.compiling or not _COMPILE_JIT:
                return func(*args, **kwargs)

            if (
                self.backend_func
                and error
                and error.startswith("Invalid call to pythranized function `")
            ):
                logger.debug(error)
                logger.info(
                    f"{backend.name_capitalized} function `{func_name}` called with new types."
                )
                logger.debug(
                    "Transonic is going to recompute the function for the new types."
                )

            arg_types = [
                backend.jit.compute_typename_from_object(arg)
                for arg in itertools.chain(args, kwargs.values())
            ]

            backenize_with_new_header(arg_types)
            return func(*args, **kwargs)

        return type_collector
