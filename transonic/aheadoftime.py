"""User runtime API for the ahead-of-time compilation
=====================================================

User API
--------

.. autofunction:: boost

.. autoclass:: Transonic
   :members:
   :private-members:

Internal API
------------

.. autofunction:: _get_transonic_calling_module

.. autoclass:: CheckCompiling
   :members:
   :private-members:

"""

import inspect
import time
import subprocess
import os
import functools
import sys

from warnings import warn

from .util import (
    get_module_name,
    has_to_compile_at_import,
    import_from_path,
    has_to_build,
    modification_date,
    is_method,
    path_jit_classes,
    write_if_has_to_write,
)

from transonic.compiler import (
    compile_extension,
    name_ext_from_path_backend,
    ext_suffix,
)
from transonic.transpiler import produce_code_class

from .log import logger
from . import mpi
from .mpi import Path
from .config import has_to_replace

if mpi.nb_proc == 1:
    mpi.has_to_build = has_to_build
    mpi.modification_date = modification_date

is_transpiling = False
modules = {}

path_jit_classes = mpi.Path(path_jit_classes)


def _get_transonic_calling_module(index_frame: int = 2):
    """Get the Transonic instance corresponding to the calling module

    Parameters
    ----------

    index_frame : int

      Index (in :code:`inspect.stack()`) of the frame to be selected

    """

    try:
        frame = inspect.stack()[index_frame]
    except IndexError:
        print("index_frame", index_frame)
        print([frame[1] for frame in inspect.stack()])
        raise

    module_name = get_module_name(frame)

    if module_name in modules:
        ts = modules[module_name]
        if (
            ts.is_transpiling != is_transpiling
            or ts._compile_at_import_at_creation != has_to_compile_at_import()
            or hasattr(ts, "path_mod")
            and ts.path_mod.exists()
            and mpi.has_to_build(ts.path_pythran, ts.path_mod)
        ):
            ts = Transonic(frame=frame, reuse=False)
    else:
        ts = Transonic(frame=frame, reuse=False)

    return ts


def boost(obj):
    """Decorator to declare that an object can "use" pythran

    Parameters
    ----------

    obj: a function, a method or a class

    """

    ts = _get_transonic_calling_module()
    return ts.boost(obj)


class CheckCompiling:
    """Check if the module is being compiled and replace the module and the function"""

    def __init__(self, ts, func):
        self.has_been_replaced = False
        self.ts = ts
        self.func = func

    def __call__(self, *args, **kwargs):

        if self.has_been_replaced:
            return self.func(*args, **kwargs)

        ts = self.ts
        if ts.is_compiling and not ts.process.is_alive():
            ts.is_compiling = False
            time.sleep(0.1)
            ts.module_pythran = import_from_path(
                ts.path_extension, ts.module_pythran.__name__
            )
            assert hasattr(self.ts.module_pythran, "__pythran__")
            ts.is_compiled = True

        if not ts.is_compiling:
            self.func = getattr(ts.module_pythran, self.func.__name__)
            self.has_been_replaced = True

        return self.func(*args, **kwargs)


class Transonic:
    """
    Representation of a module using ahead-of-time transonic commands

    Parameters
    ----------

    use_transonified : bool (optional, default True)

      If False, don't use the pythranized versions at run time

    frame : int (optional)

      (Internal) Index (in :code:`inspect.stack()`) of the frame to be selected

    reuse : bool (optional, default True)

      (Internal) If True, do not recreate an instance.

    """

    def __init__(self, use_transonified=True, frame=None, reuse=True):
        from transonic.config import backend_default

        if frame is None:
            frame = inspect.stack()[1]

        self.module_name = module_name = get_module_name(frame)

        self._compile_at_import_at_creation = has_to_compile_at_import()

        if reuse and module_name in modules:
            ts = modules[module_name]
            for key, value in ts.__dict__.items():
                self.__dict__[key] = value
            return

        self.names_template_variables = {}

        self.is_transpiling = is_transpiling
        self.has_to_replace = has_to_replace

        if is_transpiling:
            self.functions = {}
            self.classes = {}
            self.signatures_func = {}
            self.is_transpiled = False
            self.is_compiled = False
            return

        self.is_compiling = False

        if not use_transonified or not has_to_replace:
            self.is_transpiled = False
            self.is_compiled = False
            return

        if "." in module_name:
            package, module_short_name = module_name.rsplit(".", 1)
            module_pythran_name = package + "."
        else:
            module_short_name = module_name
            module_pythran_name = ""

        module_pythran_name += "__pythran__." + module_short_name

        self.path_mod = path_mod = Path(frame.filename)
        self.path_pythran = path_pythran = (
            path_mod.parent / "__pythran__" / (module_short_name + ".py")
        )

        path_ext = None

        if has_to_compile_at_import() and path_mod.exists():
            if mpi.has_to_build(path_pythran, path_mod):
                if path_pythran.exists():
                    time_pythran = mpi.modification_date(path_pythran)
                else:
                    time_pythran = 0

                returncode = None
                if mpi.rank == 0:
                    print(f"Running transonic on file {path_mod}... ", end="")
                    # better to do this in another process because the file is already run...
                    os.environ["TRANSONIC_NO_MPI"] = "1"
                    returncode = subprocess.call(
                        [
                            sys.executable,
                            "-m",
                            "transonic.run",
                            "-np",
                            str(path_mod),
                        ]
                    )
                    del os.environ["TRANSONIC_NO_MPI"]
                returncode = mpi.bcast(returncode)

                if returncode != 0:
                    raise RuntimeError(
                        "transonic does not manage to produce the Pythran "
                        f"file for {path_mod}"
                    )

                if mpi.rank == 0:
                    print("Done!")

                path_ext = path_pythran.with_name(
                    name_ext_from_path_backend(path_pythran)
                )

                time_pythran_after = mpi.modification_date(path_pythran)
                # We have to touch the files to signal that they are up-to-date
                if time_pythran_after == time_pythran and mpi.rank == 0:
                    if not has_to_build(path_ext, path_pythran):
                        path_pythran.touch()
                        if path_ext.exists():
                            path_ext.touch()
                    else:
                        path_pythran.touch()

        path_ext = path_ext or path_pythran.with_name(
            name_ext_from_path_backend(path_pythran)
        )

        self.path_extension = path_ext
        if (
            has_to_compile_at_import()
            and path_mod.exists()
            and not self.path_extension.exists()
        ):
            if mpi.rank == 0:
                print("Launching Pythran to compile a new extension...")
            self.process = compile_extension(
                path_pythran,
                backend_default,
                name_ext_file=self.path_extension.name,
            )
            self.is_compiling = True
            self.is_compiled = False

        self.is_transpiled = True

        if not path_ext.exists() and not self.is_compiling:
            path_ext_alt = path_pythran.with_suffix(ext_suffix)
            if path_ext_alt.exists():
                self.path_extension = path_ext = path_ext_alt

        self.reload_module_pythran(module_pythran_name)

        if self.is_transpiled:
            self.is_compiled = hasattr(self.module_pythran, "__pythran__")
            if self.is_compiled:
                module = inspect.getmodule(frame[0])
                # module can be None if (at least) it has been run with runpy
                if module is not None:
                    module.__pythran__ = self.module_pythran.__pythran__
                    module.__transonic__ = self.module_pythran.__transonic__

            if hasattr(self.module_pythran, "arguments_blocks"):
                self.arguments_blocks = getattr(
                    self.module_pythran, "arguments_blocks"
                )

        modules[module_name] = self

    def reload_module_pythran(self, module_pythran_name=None):
        if module_pythran_name is None:
            module_pythran_name = self.module_pythran.__name__
        if self.path_extension.exists() and not self.is_compiling:
            self.module_pythran = import_from_path(
                self.path_extension, module_pythran_name
            )
        elif self.path_pythran.exists():
            self.module_pythran = import_from_path(
                self.path_pythran, module_pythran_name
            )
        else:
            self.is_transpiled = False
            self.is_compiled = False

    def transonic_def(self, func):
        """Decorator used for functions

        Parameters
        ----------

        func: a function

        """
        if is_method(func):
            return self.transonic_def_method(func)

        if is_transpiling or not has_to_replace or not self.is_transpiled:
            return func

        if not hasattr(self.module_pythran, func.__name__):
            self.reload_module_pythran()

        try:
            func_tmp = getattr(self.module_pythran, func.__name__)
        except AttributeError:
            logger.warning(
                "Pythran file does not seem to be up-to-date:\n"
                f"{self.module_pythran}\nfunc: {func.__name__}"
            )
            func_tmp = func

        if self.is_compiling:
            return functools.wraps(func)(CheckCompiling(self, func_tmp))

        return func_tmp

    def transonic_def_method(self, func):
        """Decorator used for methods

        Parameters
        ----------

        func: a function

        """

        if is_transpiling or not has_to_replace or not self.is_transpiled:
            return func

        return TransonicTemporaryMethod(func)

    def boost(self, obj):
        """Universal decorator for AOT compilation

        Used for functions, methods and classes.
        """
        if isinstance(obj, type):
            return self.transonic_class(obj)
        else:
            return self.transonic_def(obj)

    def transonic_class(self, cls: type):
        """Decorator used for classes

        Parameters
        ----------

        cls: a class

        """
        if is_transpiling:
            return cls

        jit_methods = {
            key: value
            for key, value in cls.__dict__.items()
            if isinstance(value, TransonicTemporaryJITMethod)
        }

        if jit_methods:
            cls = jit_class(cls, jit_methods)

        if not has_to_replace or not self.is_transpiled:
            return cls

        cls_name = cls.__name__

        for key, value in cls.__dict__.items():
            if not isinstance(value, TransonicTemporaryMethod):
                continue
            func = value.func
            func_name = func.__name__

            name_pythran_func = f"__for_method__{cls_name}__{func_name}"
            name_var_code_new_method = (
                f"__code_new_method__{cls_name}__{func_name}"
            )

            if not hasattr(self.module_pythran, name_pythran_func):
                self.reload_module_pythran()

            try:
                pythran_func = getattr(self.module_pythran, name_pythran_func)
                code_new_method = getattr(
                    self.module_pythran, name_var_code_new_method
                )
            except AttributeError:
                logger.warning("Pythran file does not seem to be up-to-date.")
                # setattr(cls, key, func)
            else:
                namespace = {"pythran_func": pythran_func}
                exec(code_new_method, namespace)
                setattr(cls, key, functools.wraps(func)(namespace["new_method"]))

        return cls

    def use_block(self, name):
        """Use the pythranized version of a code block

        Parameters
        ----------

        name : str

          The name of the block.

        """
        if not self.is_transpiled:
            raise ValueError(
                "`use_block` has to be used protected by `if ts.is_transpiled`"
            )

        if self.is_compiling and not self.process.is_alive():
            self.is_compiling = False
            time.sleep(0.1)
            self.module_pythran = import_from_path(
                self.path_extension, self.module_pythran.__name__
            )
            assert hasattr(self.module_pythran, "__pythran__")
            self.is_compiled = True

        func = getattr(self.module_pythran, name)
        argument_names = self.arguments_blocks[name]

        frame = inspect.currentframe()
        try:
            locals_caller = frame.f_back.f_locals
        finally:
            del frame

        arguments = [locals_caller[name] for name in argument_names]
        return func(*arguments)

    def include(self, func):
        warn(
            "include is obsolete and will be removed in transonic 0.2",
            DeprecationWarning,
        )


class TransonicTemporaryMethod:
    """Internal temporary class for methods"""

    def __init__(self, func):
        self.func = func

    def __call__(self, self_bis, *args, **kwargs):
        raise RuntimeError(
            "Did you forget to decorate a class using methods decorated "
            "with transonic? Please decorate it with @boost."
        )


def include(func=None, used_by=None):
    warn(
        "include is obsolete and will be removed in transonic 0.2",
        DeprecationWarning,
    )


class TransonicTemporaryJITMethod:
    """Internal temporary class for JIT methods"""

    __transonic__ = "jit_method"

    def __init__(self, func, native, xsimd, openmp):
        self.func = func
        self.native = native
        self.xsimd = xsimd
        self.openmp = openmp

    def __call__(self, self_bis, *args, **kwargs):
        raise RuntimeError(
            "Did you forget to decorate a class using methods decorated "
            "with transonic? Please decorate it with @boost."
        )


def jit_class(cls, jit_methods):
    """Modify the class by replacing jit methods

    1. create a Python file with @jit functions and methods
    2. import the file
    3. replace the methods

    """
    if not has_to_replace:
        return cls

    cls_name = cls.__name__
    mod_name = cls.__module__

    module = sys.modules[mod_name]

    # 1. create a Python file with @jit functions and methods
    python_path_dir = path_jit_classes / mod_name.replace(".", os.path.sep)
    python_path = python_path_dir / (cls_name + ".py")

    if mpi.has_to_build(python_path, module.__file__):
        from transonic.justintime import _get_module_jit

        mod = _get_module_jit(backend="pythran", index_frame=5)
        if mpi.rank == 0:
            python_path = mpi.PathSeq(python_path)
            python_code = mod.codes_dependance_classes[cls_name] + "\n"
            python_code += produce_code_class(cls, jit=True)
            write_if_has_to_write(python_path, python_code)
            python_path = mpi.Path(python_path)
        mpi.barrier()

    # 2. import the file
    python_mod_name = path_jit_classes.name + "." + mod_name + "." + cls_name
    module = import_from_path(python_path, python_mod_name)

    # 3. replace the methods
    for name_method, method in jit_methods.items():
        func = method.func
        name_new_method = f"__new_method__{cls.__name__}__{name_method}"
        new_method = getattr(module, name_new_method)
        setattr(cls, name_method, functools.wraps(func)(new_method))

    return cls
