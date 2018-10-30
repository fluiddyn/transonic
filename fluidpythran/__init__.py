import inspect
import importlib.util
import itertools
from ._version import __version__

try:
    from ._path_data_tests import path_data_tests
except ImportError:
    pass


def _get_fluidpythran_object(index_frame=2):

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
            fp = FluidPythran(frame=frame)
    else:
        fp = FluidPythran(frame=frame)

    return fp


from .annotation import Array, NDim, Type, Shape

__all__ = [
    "__version__",
    "FluidPythran",
    "path_data_tests",
    "Array",
    "NDim",
    "Type",
    "Shape",
]

is_compiling = False


_modules = {}


def pythran_def(func):

    fp = _get_fluidpythran_object()
    return fp.pythran_def(func)


def make_signature(func, **kwargs):

    if not is_compiling:
        return

    fp = _get_fluidpythran_object()
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
        """Decorator used for functions"""

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

        if _signature is None:
            _signature = inspect.signature(func)

        signature = f"{func.__name__}("
        pythran_types = []
        for k, p in _signature.parameters.items():
            try:
                pythran_type = p.annotation.get_pythran_type(**kwargs)
            except AttributeError:
                pythran_type = p.annotation.__name__

            pythran_types.append(pythran_type)

        signature += ", ".join(pythran_types) + ")"

        if func.__name__ not in self.signatures_func:
            self.signatures_func[func.__name__] = []

        self.signatures_func[func.__name__].append(signature)

    def _make_signatures_from_annotations(self):

        for func in self.functions.values():

            annotations = func.__annotations__

            if not annotations:
                continue

            _signature = inspect.signature(func)

            template_parameters = []

            for annotation in annotations.values():
                if hasattr(annotation, "get_template_parameters"):
                    template_parameters.extend(
                        annotation.get_template_parameters()
                    )

            template_parameters = set(template_parameters)

            if not template_parameters:
                self.make_signature(func, _signature=_signature)
                continue

            if not all(param.values for param in template_parameters):
                continue

            values = {}
            for param in template_parameters:
                values[param.__name__] = param.values

            names = values.keys()
            for set_values in itertools.product(*values.values()):
                template_variables = {
                    name: value for name, value in zip(names, set_values)
                }
                self.make_signature(
                    func, _signature=_signature, **template_variables
                )

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
