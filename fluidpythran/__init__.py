
import inspect
import importlib

from ._version import __version__

from .toolchain import create_pythran_code, create_pythran_file

__all__ = [
    "__version__",
    "create_pythran_code",
    "create_pythran_file",
    "FluidPythran",
]


class FluidPythran:
    def __init__(self, use_pythran=True):

        if not use_pythran:
            self.is_pythranized = False
            return

        frame = inspect.stack()[1]
        module_name = inspect.getmodulename(frame.filename)
        module_pythran_name = "_pythran._pythran_" + module_name

        try:
            self.module_pythran = importlib.import_module(module_pythran_name)
            self.is_pythranized = True
        except ModuleNotFoundError:
            self.is_pythranized = False
        else:
            self.arguments_blocks = getattr(
                self.module_pythran, "arguments_blocks"
            )

    def monkey_patch_function(self, func):

        if self.is_pythranized:
            return getattr(self.module_pythran, func.__name__)
        else:
            return func

    def use_pythranized_block(self, name):

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
