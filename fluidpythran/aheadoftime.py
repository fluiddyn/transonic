"""User runtime API for the ahead-of-time compilation
=====================================================

User API
--------

.. autofunction:: boost

.. autofunction:: make_signature

.. autoclass:: FluidPythran
   :members:
   :private-members:

.. autofunction:: pythran_def

Internal API
------------

.. autofunction:: _get_fluidpythran_calling_module

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
    has_to_pythranize_at_import,
    import_from_path,
    has_to_build,
    modification_date,
    is_method,
    path_cachedjit_classes,
)

from .pythranizer import (
    compile_pythran_file,
    name_ext_from_path_pythran,
    ext_suffix,
)

from .annotation import (
    make_signature_from_template_variables,
    make_signatures_from_typehinted_func,
)

from .transpiler import produce_code_class

from .log import logger
from . import mpi
from .mpi import Path
from .config import has_to_replace

if mpi.nb_proc == 1:
    mpi.has_to_build = has_to_build
    mpi.modification_date = modification_date

is_transpiling = False
modules = {}

path_cachedjit_classes = mpi.Path(path_cachedjit_classes)


def _get_fluidpythran_calling_module(index_frame: int = 2):
    """Get the FluidPythran instance corresponding to the calling module

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
        fp = modules[module_name]
        if (
            fp.is_transpiling != is_transpiling
            or fp._pythranize_at_import_at_creation
            != has_to_pythranize_at_import()
            or hasattr(fp, "path_mod")
            and fp.path_mod.exists()
            and mpi.has_to_build(fp.path_pythran, fp.path_mod)
        ):
            fp = FluidPythran(frame=frame, reuse=False)
    else:
        fp = FluidPythran(frame=frame, reuse=False)

    return fp


def pythran_def(func):
    """Decorator to declare that a pythranized version of the function has to
    be used

    ``pythran_def`` is deprecated, use ``boost`` instead

    Parameters
    ----------

    func: a function

    """
    warn("pythran_def is deprecated, use boost instead", DeprecationWarning)

    fp = _get_fluidpythran_calling_module()
    return fp.pythran_def(func)


def boost(obj):
    """Decorator to declare that an object can "use" pythran

    Parameters
    ----------

    obj: a function, a method or a class

    """

    fp = _get_fluidpythran_calling_module()
    return fp.boost(obj)


def make_signature(func, **kwargs):
    """Create signature for a function with values for the template types

    Parameters
    ----------

    func: a function

    kwargs : dict

      The template types and their value

    """
    if not is_transpiling:
        return

    fp = _get_fluidpythran_calling_module()
    fp.make_signature(func, **kwargs)


class CheckCompiling:
    """Check if the module is been compiled and replace the module and the function"""

    def __init__(self, fp, func):
        self.has_been_replaced = False
        self.fp = fp
        self.func = func

    def __call__(self, *args, **kwargs):

        if self.has_been_replaced:
            return self.func(*args, **kwargs)

        fp = self.fp
        if fp.is_compiling and not fp.process.is_alive():
            fp.is_compiling = False
            time.sleep(0.1)
            fp.module_pythran = import_from_path(
                fp.path_extension, fp.module_pythran.__name__
            )
            assert hasattr(self.fp.module_pythran, "__pythran__")
            fp.is_compiled = True

        if not fp.is_compiling:
            self.func = getattr(fp.module_pythran, self.func.__name__)
            self.has_been_replaced = True

        return self.func(*args, **kwargs)


class FluidPythran:
    """
    Representation of a module using ahead-of-time fluidpythran commands

    Parameters
    ----------

    use_fluidpythranized : bool (optional, default True)

      If False, don't use the pythranized versions at run time

    frame : int (optional)

      (Internal) Index (in :code:`inspect.stack()`) of the frame to be selected

    reuse : bool (optional, default True)

      (Internal) If True, do not recreate an instance.

    """

    def __init__(self, use_fluidpythranized=True, frame=None, reuse=True):

        if frame is None:
            frame = inspect.stack()[1]

        self.module_name = module_name = get_module_name(frame)

        self._pythranize_at_import_at_creation = has_to_pythranize_at_import()

        if reuse and module_name in modules:
            fp = modules[module_name]
            for key, value in fp.__dict__.items():
                self.__dict__[key] = value
            return

        self.names_template_variables = {}

        self.is_transpiling = is_transpiling

        if is_transpiling:
            self.functions = {}
            self.classes = {}
            self.signatures_func = {}
            self.included_functions = []
            modules[module_name] = self
            self.is_transpiled = False
            return

        if not use_fluidpythranized or not has_to_replace:
            self.is_transpiled = False
            return

        self.is_compiling = False

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

        if has_to_pythranize_at_import() and path_mod.exists():
            if mpi.has_to_build(path_pythran, path_mod):
                if path_pythran.exists():
                    time_pythran = mpi.modification_date(path_pythran)
                else:
                    time_pythran = 0

                returncode = None
                if mpi.rank == 0:
                    print(f"Running fluidpythran on file {path_mod}... ", end="")
                    # better to do this in another process because the file is already run...
                    os.environ["FLUIDPYTHRAN_NO_MPI"] = "1"
                    returncode = subprocess.call(
                        [
                            sys.executable,
                            "-m",
                            "fluidpythran.run",
                            "-np",
                            str(path_mod),
                        ]
                    )
                    del os.environ["FLUIDPYTHRAN_NO_MPI"]
                returncode = mpi.bcast(returncode)

                if returncode != 0:
                    raise RuntimeError(
                        "fluidpythran does not manage to produce the Pythran "
                        f"file for {path_mod}"
                    )

                if mpi.rank == 0:
                    print("Done!")

                path_ext = path_pythran.with_name(
                    name_ext_from_path_pythran(path_pythran)
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
            name_ext_from_path_pythran(path_pythran)
        )

        self.path_extension = path_ext

        if (
            has_to_pythranize_at_import()
            and path_mod.exists()
            and not self.path_extension.exists()
        ):
            if mpi.rank == 0:
                print("Launching Pythran to compile a new extension...")
            self.process = compile_pythran_file(
                path_pythran, name_ext_file=self.path_extension.name
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
                    module.__fluidpythran__ = self.module_pythran.__fluidpythran__

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

    def pythran_def(self, func):
        """Decorator used for functions

        Parameters
        ----------

        func: a function

        """
        if is_method(func):
            return self.pythran_def_method(func)

        if is_transpiling:
            self.functions[func.__name__] = func
            return func

        if not has_to_replace or not self.is_transpiled:
            return func

        if not hasattr(self.module_pythran, func.__name__):
            self.reload_module_pythran()

        try:
            func_tmp = getattr(self.module_pythran, func.__name__)
        except AttributeError:
            logger.warning("Pythran file does not seem to be up-to-date.")
            func_tmp = func

        if self.is_compiling:
            return functools.wraps(func)(CheckCompiling(self, func_tmp))

        return func_tmp

    def pythran_def_method(self, func):
        """Decorator used for methods

        Parameters
        ----------

        func: a function

        """
        if is_transpiling:
            func.__fluidpythran__ = "pythran_def_method"
            return func

        if not has_to_replace or not self.is_transpiled:
            return func

        return FluidPythranTemporaryMethod(func)

    def boost(self, obj):
        """Universal decorator for AOT compilation

        Used for functions, methods and classes.
        """
        if isinstance(obj, type):
            return self.pythran_class(obj)
        else:
            return self.pythran_def(obj)

    def pythran_class(self, cls: type):
        """Decorator used for classes

        Parameters
        ----------

        cls: a class

        """
        if is_transpiling:
            self.classes[cls.__name__] = cls
            return cls

        jit_methods = {
            key: value
            for key, value in cls.__dict__.items()
            if isinstance(value, FluidPythranTemporaryJITMethod)
        }

        if jit_methods:
            cls = cachedjit_class(cls, jit_methods)

        if not has_to_replace or not self.is_transpiled:
            return cls

        cls_name = cls.__name__

        for key, value in cls.__dict__.items():
            if not isinstance(value, FluidPythranTemporaryMethod):
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

    def make_signature(self, func, _signature=None, **kwargs):
        """Create signature for a function with values for the template types

        Parameters
        ----------

        func: a function

        kwargs : dict

          The template types and their value

        """
        signature = make_signature_from_template_variables(
            func, _signature=_signature, **kwargs
        )

        if func.__name__ not in self.signatures_func:
            self.signatures_func[func.__name__] = []

        self.signatures_func[func.__name__].append(signature)

    def use_pythranized_block(self, name):
        """Use the pythranized version of a code block

        Parameters
        ----------

        name : str

          The name of the block.

        """
        if not self.is_transpiled:
            raise ValueError(
                "`use_pythranized_block` has to be used protected "
                "by `if fp.is_transpiled`"
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

    def _make_signatures_from_annotations(self):
        """Make the signatures from annotations if it is possible

        Useful when there are only "not templated" types.

        """
        for func in self.functions.values():
            signatures = make_signatures_from_typehinted_func(func)
            if func.__name__ not in self.signatures_func:
                self.signatures_func[func.__name__] = []
            self.signatures_func[func.__name__].extend(signatures)

    def include(self, func):
        self.included_functions.append(func)


class FluidPythranTemporaryMethod:
    """Internal temporary class for methods"""

    def __init__(self, func):
        self.func = func

    def __call__(self, self_bis, *args, **kwargs):
        raise RuntimeError(
            "Did you forget to decorate a class using methods decorated "
            "with fluidpythran? Please decorate it with @boost."
        )


def include(func=None, used_by=None):
    """Decorator to record that the function has to be included in a Pythran file

    """
    if func is not None and used_by is None:
        if not callable(func):
            func, used_by = used_by, func

    decor = Include(used_by=used_by)
    if callable(func):
        decor._decorator_no_arg = True
        return decor(func)
    else:
        return decor


class Include:
    """Decorator used internally by the public include decorator

    @include

    @include(used_by=("func0", "func1")

    """

    def __init__(self, used_by=None):
        self.used_by = used_by
        self._decorator_no_arg = False

    def __call__(self, func):

        if self._decorator_no_arg:
            index_frame = 3
        else:
            index_frame = 2

        if self.used_by is not None:
            from .justintime import _get_module_cachedjit

            jit_mod = _get_module_cachedjit(index_frame)
            jit_mod.record_used_function(func, self.used_by)

        if not is_transpiling:
            return func

        fp = _get_fluidpythran_calling_module(index_frame)
        fp.include(func)
        return func


class FluidPythranTemporaryJITMethod:
    """Internal temporary class for JIT methods"""

    __fluidpythran__ = "jit_method"

    def __init__(self, func, native, xsimd, openmp):
        self.func = func
        self.native = native
        self.xsimd = xsimd
        self.openmp = openmp

    def __call__(self, self_bis, *args, **kwargs):
        raise RuntimeError(
            "Did you forget to decorate a class using methods decorated "
            "with fluidpythran? Please decorate it with @boost."
        )


def cachedjit_class(cls, jit_methods):
    """Modify the class by replacing cachedjit methods

    1. create a Python file with @cachejit functions and methods
    2. import the file
    3. replace the methods

    """
    if not has_to_replace:
        return cls

    cls_name = cls.__name__
    mod_name = cls.__module__

    module = sys.modules[mod_name]

    # 1. create a Python file with @cachejit functions and methods
    python_path_dir = path_cachedjit_classes / mod_name.replace(".", os.path.sep)
    python_path = python_path_dir / (cls_name + ".py")

    if mpi.has_to_build(python_path, module.__file__):
        if mpi.rank == 0:
            python_path = mpi.PathSeq(python_path)
            python_code = produce_code_class(cls, jit=True)

            has_to_write = None
            if python_path.exists():
                with open(python_path, "r") as file:
                    python_code_file = file.read()

                if python_code_file != python_code:
                    has_to_write = True
            else:
                has_to_write = True

            if has_to_write:
                python_path_dir.mkdir(exist_ok=True, parents=True)
                with open(python_path, "w") as file:
                    file.write(python_code)
            python_path = mpi.Path(python_path)
        mpi.barrier()

    # 2. import the file
    python_mod_name = (
        path_cachedjit_classes.name + "." + mod_name + "." + cls_name
    )
    module = import_from_path(python_path, python_mod_name)

    # 3. replace the methods
    for name_method, method in jit_methods.items():
        func = method.func
        name_new_method = f"__new_method__{cls.__name__}__{name_method}"
        new_method = getattr(module, name_new_method)
        setattr(cls, name_method, functools.wraps(func)(new_method))

    return cls
