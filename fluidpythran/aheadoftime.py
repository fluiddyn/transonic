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



"""

import inspect
import importlib.util


from .util import get_module_name

from .annotation import (
    make_signature_from_template_variables,
    make_signatures_from_typehinted_func,
)

is_compiling = False
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
        if fp._created_while_compiling != is_compiling:
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
    if not is_compiling:
        return

    fp = _get_fluidpythran_calling_module()
    fp.make_signature(func, **kwargs)


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

        self._created_while_compiling = is_compiling

        if is_compiling:
            self.functions = {}
            self.signatures_func = {}
            _modules[module_name] = self
            self.is_pythranized = False
            return

        if not use_pythran:
            self.is_pythranized = False
            return

        if "." in module_name:
            package, module = module_name.rsplit(".", 1)
            module_pythran = package + "._pythran._" + module
        else:
            module_pythran = "_pythran._" + module_name

        try:
            self.module_pythran = importlib.import_module(module_pythran)
            self.is_pythranized = True
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

        if is_compiling:
            self.functions[func.__name__] = func
            return func

        if self.is_pythranized:
            try:
                return getattr(self.module_pythran, func.__name__)
            except AttributeError:
                return func
        else:
            return func

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
