"""Create Pythran signatures from type hints
============================================

"""

import itertools
import ast

import astunparse


class TemplateVar:
    """

    T = TemplateVar("T")
    T = TemplateVar("T", int, float)

    T = TemplateVar()  # raise ValueError
    T = TemplateVar(1)  # raise TypeError

    """

    _type_values = type
    _letter = "T"

    def get_template_parameters(self):
        return (self,)

    def __init__(self, *args, _fp=None):

        if not args:
            raise ValueError

        if _fp is None:
            fp = _get_fluidpythran_object()
        else:
            fp = _fp

        if type(self) not in fp.names_template_variables:
            fp.names_template_variables[type(self)] = set()

        names_already_used = fp.names_template_variables[type(self)]

        if self._is_correct_for_name(args[0]):
            self.__name__ = args[0]
            args = args[1:]
        else:
            index_var = len(names_already_used)

            while self._letter + str(index_var) in names_already_used:
                index_var += 1

            self.__name__ = self._letter + str(index_var)

        self.values = args

        names_already_used.add(self.__name__)

        self._check_type_values()

    def _is_correct_for_name(self, arg):
        return isinstance(arg, str)

    def _check_type_values(self):
        if not all(isinstance(value, self._type_values) for value in self.values):
            raise TypeError


class Type(TemplateVar):
    def __repr__(self):
        return self.__name__

    def get_pythran_type(self, **kwargs):

        dtype = None

        for key, value in kwargs.items():
            if key == self.__name__:
                dtype = value
                break

        if dtype is None:
            raise ValueError

        return dtype.__name__


class NDim(TemplateVar):
    _type_values = int
    _letter = "N"

    def __init__(self, *args, shift=0, _fp=None):

        if _fp is None:
            _fp = _get_fluidpythran_object()

        super().__init__(*args, _fp=_fp)
        self.shift = shift

    def __repr__(self):

        name = self.__name__

        if self.shift < 0:
            name = name + f" - {abs(self.shift)}"
        elif self.shift > 0:
            name = name + f" + {abs(self.shift)}"

        return name

    def __add__(self, number):
        fp = _get_fluidpythran_object()
        return type(self)(self.__name__, *self.values, shift=number, _fp=fp)

    def __sub__(self, number):
        fp = _get_fluidpythran_object()
        return type(self)(self.__name__, *self.values, shift=-number, _fp=fp)


class Shape(TemplateVar):
    _letter = "S"
    _type_values = str, list, tuple

    def _is_correct_for_name(self, arg):
        raise NotImplementedError
        return isinstance(arg, str)


class ArrayMeta(type):
    def __getitem__(self, parameters):

        dtype = None
        ndim = None
        for param in parameters:
            if isinstance(param, Type):
                if dtype is not None:
                    raise ValueError
            dtype = param

            if isinstance(param, NDim):
                if ndim is not None:
                    raise ValueError
                ndim = param

        parameters = {p.__name__: p for p in parameters}

        ArrayBis = type(
            "ArrayBis",
            (Array,),
            {"dtype": dtype, "ndim": ndim, "parameters": parameters},
        )

        return ArrayBis

    def get_parameters(self):
        return getattr(self, "parameters", tuple())

    def get_template_parameters(self):
        return tuple(
            param
            for param in self.get_parameters().values()
            if isinstance(param, TemplateVar)
        )

    def __repr__(self):
        strings = []
        for p in self.parameters.values():
            if isinstance(p, type):
                string = p.__name__
            else:
                string = repr(p)
            strings.append(string)

        return "Array[" + ", ".join(strings) + "]"

    def get_pythran_type(self, **kwargs):

        dtype = ndim = None

        for var in self.parameters.values():
            if isinstance(var, Type) and var.values:
                dtype = var.values[0]
            elif isinstance(var, NDim) and var.values:
                ndim = var.values[0]
            elif isinstance(var, type):
                dtype = var

        for key, value in kwargs.items():
            try:
                template_var = self.parameters[key]
            except KeyError:
                continue

            if isinstance(template_var, Type):
                dtype = value
            elif isinstance(template_var, NDim):
                ndim = value + template_var.shift
            else:
                raise ValueError

        if dtype is None or ndim is None:
            raise ValueError

        if ndim == 0:
            raise NotImplementedError

        return f"{dtype.__name__}[{', '.join([':']*ndim)}]"


class Array(metaclass=ArrayMeta):
    pass


def compute_pythran_types_from_types(types, **kwargs):
    pythran_types = []
    for type_ in types:
        try:
            pythran_type = type_.get_pythran_type(**kwargs)
        except AttributeError:
            pythran_type = type_.__name__

        pythran_types.append(pythran_type)

    return pythran_types


def compute_pythran_types_from_valued_types(types):
    template_parameters = []

    for type_ in types:
        if hasattr(type_, "get_template_parameters"):
            template_parameters.extend(type_.get_template_parameters())

    template_parameters = set(template_parameters)

    if not template_parameters:
        str_types = []
        for type_ in types:
            if isinstance(type_, type):
                str_type = type_.__name__
            else:
                str_type = type_
            str_types.append(str_type)
        return (str_types,)

    if not all(param.values for param in template_parameters):
        raise ValueError

    values_template_parameters = {}
    for param in template_parameters:
        values_template_parameters[param.__name__] = param.values

    pythran_types = []
    names = values_template_parameters.keys()
    for set_types in itertools.product(*values_template_parameters.values()):
        template_variables = {
            name: value for name, value in zip(names, set_types)
        }

        pythran_types.append(
            compute_pythran_types_from_types(types, **template_variables)
        )

    return pythran_types


class TypeHintRemover(ast.NodeTransformer):
    """

    from https://stackoverflow.com/a/42734810/1779806
    """

    def visit_FunctionDef(self, node):
        # remove the return type defintion
        node.returns = None
        # remove all argument annotations
        if node.args.args:
            for arg in node.args.args:
                arg.annotation = None
        return node


def strip_typehints(source):
    # parse the source code into an AST
    parsed_source = ast.parse(source)
    # remove all type annotations, function return type definitions
    # and import statements from 'typing'
    transformed = TypeHintRemover().visit(parsed_source)
    # convert the AST back to source code
    return astunparse.unparse(transformed)


# we need to put this import here
from .aheadoftime import _get_fluidpythran_object
