"""User runtime API for the ahead-of-time compilation
=====================================================

User API
--------

.. autofunction:: pythran_def

.. autofunction:: make_signature

.. autoclass:: FluidPythran
   :members:
   :private-members:

Internal API
------------

.. autofunction:: _get_fluidpythran_calling_module

.. autoclass:: CheckCompiling
   :members:
   :private-members:

"""

import inspect
import importlib.util
import time
from pathlib import Path

from .util import (
    get_module_name,
    compile_pythran_file,
    has_to_pythranize_at_import,
    import_from_path,
    ext_suffix,
    has_to_build,
)

from .annotation import (
    make_signature_from_template_variables,
    make_signatures_from_typehinted_func,
)

from .log import logger

is_transpiling = False
_modules = {}


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

    if module_name in _modules:
        fp = _modules[module_name]
        if fp._created_while_transpiling != is_transpiling:
            fp = FluidPythran(frame=frame, reuse=False)
    else:
        fp = FluidPythran(frame=frame, reuse=False)

    return fp


def pythran_def(func):
    """Decorator to declare that a pythranized version of the function has to
    be used

    Parameters
    ----------

    func: a function

    """

    fp = _get_fluidpythran_calling_module()
    return fp.pythran_def(func)


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
        if fp.is_compiling and fp.process.poll() is not None:
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

    use_pythran : bool (optional, default True)

      If False, don't use the pythranized versions at run time

    frame : int (optional)

      (Internal) Index (in :code:`inspect.stack()`) of the frame to be selected

    reuse : bool (optional, default True)

      (Internal) If True, do not recreate an instance.

    """

    def __init__(self, use_pythran=True, frame=None, reuse=True):

        if frame is None:
            frame = inspect.stack()[1]

        module_name = get_module_name(frame)

        if reuse and module_name in _modules:
            fp = _modules[module_name]
            for key, value in fp.__dict__.items():
                self.__dict__[key] = value
            return

        self.names_template_variables = {}

        self._created_while_transpiling = is_transpiling

        if is_transpiling:
            self.functions = {}
            self.signatures_func = {}
            _modules[module_name] = self
            self.is_pythranized = False
            return

        if not use_pythran:
            self.is_pythranized = False
            return

        self.is_compiling = False

        if "." in module_name:
            package, module = module_name.rsplit(".", 1)
            module_pythran = package + ".__pythran__._" + module
        else:
            module_pythran = "__pythran__._" + module_name

        try:
            self.module_pythran = importlib.import_module(module_pythran)
            self.is_pythranized = True

            self.is_compiled = hasattr(self.module_pythran, "__pythran__")
            self.is_compiling = False

            if has_to_pythranize_at_import():
                path_pythran_file = self.module_pythran.__file__
                self.path_extension = Path(path_pythran_file).with_suffix(
                    ext_suffix
                )
                if has_to_build(self.path_extension, path_pythran_file):
                    self.process = compile_pythran_file(path_pythran_file)
                    self.is_compiling = True
                    self.is_compiled = False

            try:
                module.__pythran__ = self.module_pythran.__pythran__
            except AttributeError:
                pass
            try:
                module.__fluidpythran__ = self.module_pythran.__fluidpythran__
            except AttributeError:
                pass
        except ModuleNotFoundError:
            self.is_pythranized = False
            self.is_compiled = False
        else:
            if hasattr(self.module_pythran, "arguments_blocks"):
                self.arguments_blocks = getattr(
                    self.module_pythran, "arguments_blocks"
                )

        _modules[module_name] = self

    def pythran_def(self, func):
        """Decorator used for functions

        Parameters
        ----------

        func: a function

        """

        if is_transpiling:
            self.functions[func.__name__] = func
            return func

        if not self.is_pythranized:
            return func

        try:
            func_tmp = getattr(self.module_pythran, func.__name__)
        except AttributeError:
            logger.warning("Pythran file does not seem to be up-to-date.")
            func_tmp = func

        if self.is_compiling:
            return CheckCompiling(self, func_tmp)

        return func_tmp

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
        if not self.is_pythranized:
            raise ValueError(
                "`use_pythranized_block` has to be used protected "
                "by `if fp.is_pythranized`"
            )

        if self.is_compiling and self.process.poll() is not None:
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
