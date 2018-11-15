"""Cached JIT compilation
=========================

User API
--------

.. autofunction:: cachedjit

.. autofunction:: used_by_cachedjit

.. todo::

   It should also be possible to use type hints to get at the first compilation
   more than one signature.

Internal API
------------

.. autoclass:: ModuleCachedJIT
   :members:
   :private-members:

.. autofunction:: _get_module_cachedjit

.. autoclass:: CachedJIT
   :members:
   :private-members:

.. autofunction:: make_pythran_type_name

Notes
-----

Serge talked about @cachedjit (see https://gist.github.com/serge-sans-paille/28c86d2b33cd561ba5e50081716b2cf4)

It's indeed a good idea!

With "# pythran import" and @used_by_cachedjit the implementation isn't
too complicated.

- At import time, we create one .py file per cachedjit function.

- At run time, we create (and complete when needed) a corresponding
  .pythran file with signature(s).

  The cachedjit decorator:

  * at the first call, get the types, create the .pythran file and call
    Pythran.

  * then, try to call the pythran function and if it fails with
    a Pythran TypeError, correct the .pythran file and recompile.

Note: During the compilation (the "warmup" of the JIT), the Python function is
used.

"""

import inspect
import itertools
from pathlib import Path
import sys
import importlib
import subprocess

try:
    import pythran
except ImportError:
    pythran = False

from .util import get_module_name, has_to_build, get_source_without_decorator

modules = {}


path_root = Path.home() / ".fluidpythran"
# weird name to avoid name collision
path_cachedjit = path_root / "_fp_cachedjit"
path_cachedjit.mkdir(parents=True, exist_ok=True)


class ModuleCachedJIT:
    """Representation of a module using cachedjit"""

    def __init__(self, frame=None):

        if frame is None:
            frame = inspect.stack()[1]

        self.filename = frame.filename
        self.module_name = get_module_name(frame)
        modules[self.module_name] = self
        self.used_functions = {}
        self.cachedjit_functions = {}

    def record_used_function(self, func, names):
        if isinstance(names, str):
            names = (names,)

        for name in names:
            if name in self.used_functions:
                self.used_functions[name].append(func)
            else:
                self.used_functions[name] = [func]

    def get_source(self):
        try:
            mod = sys.modules[self.module_name]
        except KeyError:
            with open(self.filename) as file:
                return file.read()
        else:
            return inspect.getsource(mod)


def _get_module_cachedjit(index_frame: int = 2):
    """Get the ModuleCachedJIT instance corresponding to the calling module

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
        return modules[module_name]
    else:
        return ModuleCachedJIT(frame=frame)


class used_by_cachedjit:
    """Decorator to record that the function is used by a cachedjited function"""

    def __init__(self, names):
        self.names = names

    def __call__(self, func):
        mod = _get_module_cachedjit()
        mod.record_used_function(func, self.names)
        return func


def make_pythran_type_name(obj: object):
    """return the Pythran type name"""
    name = type(obj).__name__

    if name == "ndarray":
        name = obj.dtype.name
        if obj.ndim != 0:
            name += "[" + ",".join([":"] * obj.ndim) + "]"

    if name == "list":
        if not obj:
            raise ValueError(
                "cannot determine the Pythran type from an empty list"
            )
        item_type = type(obj[0])
        # FIXME: we could check if the list is homogeneous...
        name = item_type.__name__ + " list"

    return name


def cachedjit(func=None, native=True, xsimd=True, openmp=False):
    """Decorator to record that the function has to be cachedjit compiled

    """
    decor = CachedJIT(native=native, xsimd=xsimd, openmp=openmp)
    if callable(func):
        decor._decorator_no_arg = True
        return decor(func)
    else:
        return decor


def reimport_module(name_mod):
    sys.path.insert(0, str(path_root))
    print(f"(re)import module {name_mod}")
    if name_mod in sys.modules:
        del sys.modules[name_mod]
    module_pythran = importlib.import_module(name_mod)
    sys.path.pop(0)
    return module_pythran


class CachedJIT:
    """Decorator used internally by the public cachedjit decorator
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

        # FIXME: MPI?

        if not pythran:
            return func

        func_name = func.__name__

        if self._decorator_no_arg:
            index_frame = 3
        else:
            index_frame = 2

        mod = _get_module_cachedjit(index_frame)
        mod.cachedjit_functions[func_name] = self
        module_name = mod.module_name
        print(f"Make new function to replace {func_name} ({module_name})")

        path_pythran = path_cachedjit / module_name.replace(".", "__")
        path_pythran.mkdir(exist_ok=True)

        path_pythran = (path_pythran / func_name).with_suffix(".py")

        if path_pythran.exists():
            if has_to_build(path_pythran, mod.filename):
                has_to_write = True
            else:
                has_to_write = False
        else:
            has_to_write = True

        if has_to_write:
            import_lines = [
                line.split("# pythran ")[1]
                for line in mod.get_source().split("\n")
                if line.startswith("# pythran ") and "import" in line
            ]
            src = "\n".join(import_lines) + "\n"

            src += get_source_without_decorator(func)

            if func_name in mod.used_functions:
                functions = mod.used_functions[func_name]
                for function in functions:
                    src += "\n" + get_source_without_decorator(function)

            if path_pythran.exists():
                with open(path_pythran) as file:
                    src_old = file.read()
                if src_old == src:
                    has_to_write = False

            if has_to_write:
                print(f"write code in file {path_pythran}")
                with open(path_pythran, "w") as file:
                    file.write(src)

        name_mod = ".".join(
            path_pythran.absolute().relative_to(path_root).with_suffix("").parts
        )

        module_pythran = reimport_module(name_mod)

        if hasattr(module_pythran, "__pythran__"):
            print(f"module {module_pythran.__name__} already pythranized")
            self.pythran_func = getattr(module_pythran, func_name)

        if has_to_build(module_pythran.__file__, path_pythran):
            self.pythran_func = None

        path_pythran_header = path_pythran.with_suffix(".pythran")

        def type_collector(*args, **kwargs):

            if self.compiling:
                if self.process.poll() is not None:
                    self.compiling = False
                    module_pythran = reimport_module(name_mod)
                    assert hasattr(module_pythran, "__pythran__")
                    self.pythran_func = getattr(module_pythran, func_name)

            try:
                return self.pythran_func(*args, **kwargs)
            except TypeError:
                # need to compiled or recompile
                pass

            if self.compiling:
                return func(*args, **kwargs)

            arg_types = [
                make_pythran_type_name(arg)
                for arg in itertools.chain(args, kwargs.values())
            ]

            # FIXME: more than one header!
            # FIXME: also use the type hints!

            header = "export {}({})\n".format(func_name, ", ".join(arg_types))

            print(f"write Pythran signature in file {path_pythran_header}")
            with open(path_pythran_header, "w") as file:
                file.write(header)

            # FIXME: we have to limit the number of compilations occuring at
            #        the same time
            self.compiling = True
            words_command = ["pythran", "-v", str(path_pythran)]
            if self.native:
                words_command.append("-march=native")

            if self.xsimd:
                words_command.append("-DUSE_XSIMD")

            if self.openmp:
                words_command.append("-fopenmp")

            self.process = subprocess.Popen(
                words_command, cwd=str(path_pythran.parent)
            )
            return func(*args, **kwargs)

        return type_collector
