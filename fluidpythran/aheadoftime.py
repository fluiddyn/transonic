"""Ahead-of-time compilation
============================


"""

import inspect
import importlib.util
import itertools


from .util import get_module_name

from .annotation import compute_pythran_types_from_types


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
            fp = FluidPythran(frame=frame, reuse=False)
    else:
        fp = FluidPythran(frame=frame, reuse=False)

    return fp


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


class FluidPythran:
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

        types = [param.annotation for param in _signature.parameters.values()]

        pythran_types = compute_pythran_types_from_types(types, **kwargs)

        signature += ", ".join(pythran_types) + ")"

        if func.__name__ not in self.signatures_func:
            self.signatures_func[func.__name__] = []

        self.signatures_func[func.__name__].append(signature)

    def _make_signatures_from_annotations(self):

        for func in self.functions.values():

            annotations = func.__annotations__

            if not annotations:
                continue

            types = annotations.values()

            template_parameters = []

            for type_ in types:
                if hasattr(type_, "get_template_parameters"):
                    template_parameters.extend(type_.get_template_parameters())

            template_parameters = set(template_parameters)

            _signature = inspect.signature(func)

            if not template_parameters:
                self.make_signature(func, _signature=_signature)
                continue

            if not all(param.values for param in template_parameters):
                continue

            values_template_parameters = {}
            for param in template_parameters:
                values_template_parameters[param.__name__] = param.values

            names = values_template_parameters.keys()
            for set_types in itertools.product(
                *values_template_parameters.values()
            ):
                template_variables = {
                    name: value for name, value in zip(names, set_types)
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
