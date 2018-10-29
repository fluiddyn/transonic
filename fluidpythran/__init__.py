import inspect
import importlib.util

from ._version import __version__

try:
    from ._path_data_tests import path_data_tests
except ImportError:
    pass


from .annotation import Array, NDimVar, TypeVar

__all__ = [
    "__version__",
    "FluidPythran",
    "path_data_tests",
    "Array",
    "NDimVar",
    "TypeVar",
]

is_compiling = False


_modules = {}


def pythran_def(func):
    frame = inspect.stack()[1]
    module_name = get_module_name(frame)

    if module_name in _modules:
        fp = _modules[module_name]
    else:
        fp = FluidPythran(frame=frame)

    return fp.pythran_def(func)


def make_signature(func, **kwargs):

    if not is_compiling:
        return

    frame = inspect.stack()[1]
    module_name = get_module_name(frame)

    if module_name in _modules:
        fp = _modules[module_name]
    else:
        fp = FluidPythran(frame=frame)

    fp.make_signature(func, **kwargs)


def get_module_name(frame):
    module_name = inspect.getmodule(frame[0]).__name__
    if module_name in ("__main__", "<run_path>"):
        module_name = inspect.getmodulename(frame.filename)
    return module_name


class FluidPythran:
    def __init__(self, use_pythran=True, frame=None):

        if frame is None:
            frame = inspect.stack()[1]

        module = inspect.getmodule(frame[0])

        module_name = get_module_name(frame)

        if is_compiling:
            self.functions = {}
            self.signatures_func = {}
            _modules[module_name] = self
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
        """Decorator used for functions"""

        if is_compiling:
            self.functions[func.__name__] = func
            return func

        if self.is_pythranized:
            return getattr(self.module_pythran, func.__name__)
        else:
            return func

    def make_signature(self, func, **kwargs):

        signature = f"{func.__name__}("
        sig = inspect.signature(func)
        pythran_types = []
        for k, p in sig.parameters.items():
            try:
                pythran_type = p.annotation.get_pythran_type(**kwargs)
            except AttributeError:
                pythran_type = p.annotation.__name__

            pythran_types.append(pythran_type)

        signature += ", ".join(pythran_types) + ")"

        if func.__name__ not in self.signatures_func:
            self.signatures_func[func.__name__] = []

        self.signatures_func[func.__name__].append(signature)

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
