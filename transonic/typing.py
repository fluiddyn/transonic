"""Create Pythran signatures from type hints
============================================

User API
--------

.. autoclass:: Type
   :members:
   :private-members:

.. autoclass:: NDim
   :members:
   :private-members:

.. autoclass:: Array
   :members:
   :private-members:

.. autoclass:: List
   :members:
   :private-members:

.. autoclass:: Dict
   :members:
   :private-members:

.. autoclass:: Union
   :members:
   :private-members:

.. autofunction:: str2type

Internal API
------------

.. autoclass:: TemplateVar
   :members:
   :private-members:

.. autoclass:: ArrayMeta
   :members:
   :private-members:

.. autoclass:: ListMeta
   :members:
   :private-members:

.. autoclass:: DictMeta
   :members:
   :private-members:

.. autofunction:: format_type_as_backend_type

"""

import numpy as np

from transonic.util import get_name_calling_module

names_template_variables = {}


class TemplateVar:
    """Base class for template variables

    >>> T = TemplateVar("T")
    >>> T = TemplateVar("T", int, float)

    >>> T = TemplateVar()  # raise ValueError
    >>> T = TemplateVar(1)  # raise TypeError

    """

    _type_values = type
    _letter = "T"

    def get_template_parameters(self):
        return (self,)

    def __init__(self, *args, name_calling_module=None):

        if not args:
            raise ValueError

        if name_calling_module is None:
            name_calling_module = get_name_calling_module()
        else:
            name_calling_module = name_calling_module

        if name_calling_module not in names_template_variables:
            names_template_variables[name_calling_module] = {}

        names_variables = names_template_variables[name_calling_module]

        if type(self) not in names_variables:
            names_variables[type(self)] = set()

        names_already_used = names_variables[type(self)]

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
            raise TypeError(
                f"{self.values} "
                f"{[isinstance(value, self._type_values) for value in self.values]}"
            )


class Type(TemplateVar):
    """Template variable representing the dtype of an array"""

    def __repr__(self):
        return self.__name__

    def format_as_backend_type(self, backend_type_formatter, **kwargs):

        dtype = None

        for key, value in kwargs.items():
            if key == self.__name__:
                dtype = value
                break

        if dtype is None:
            raise ValueError

        return dtype.__name__


class NDim(TemplateVar):
    """Template variable representing the number of dimension of an array"""

    _type_values = int
    _letter = "N"

    def __init__(self, *args, shift=0, name_calling_module=None):

        if name_calling_module is None:
            name_calling_module = get_name_calling_module()

        super().__init__(*args, name_calling_module=name_calling_module)
        self.shift = shift

    def __repr__(self):

        name = self.__name__

        if self.shift < 0:
            name = name + f" - {abs(self.shift)}"
        elif self.shift > 0:
            name = name + f" + {abs(self.shift)}"

        return name

    def __add__(self, number):
        name_calling_module = get_name_calling_module()
        return type(self)(
            self.__name__,
            *self.values,
            shift=number,
            name_calling_module=name_calling_module,
        )

    def __sub__(self, number):
        name_calling_module = get_name_calling_module()
        return type(self)(
            self.__name__,
            *self.values,
            shift=-number,
            name_calling_module=name_calling_module,
        )


class UnionVar(TemplateVar):

    _type_values = type
    _letter = "U"


class ArrayMeta(type):
    """Metaclass for the Array class used for type hinname_calling_module"""

    def __getitem__(self, parameters):

        if not isinstance(parameters, tuple):
            parameters = (parameters,)

        dtype = None
        ndim = None
        memview = False
        params_filtered = []
        for param in parameters:
            if isinstance(param, (Type, type)):
                if dtype is not None:
                    raise ValueError(
                        "Array should be defined with only one variable defining "
                        "the types. For more than one type, use "
                        "for example Type(float, int)"
                    )
                dtype = param

            if isinstance(param, NDim):
                if ndim is not None:
                    raise ValueError(
                        "Array should be defined with only "
                        "one NDim. For more than one dimension, use "
                        "for example NDim(2, 3)."
                    )
                ndim = param

            if (
                isinstance(param, str)
                and param[-1] == "d"
                and param[:-1].isnumeric()
            ):
                try:
                    tmp = int(param[:-1])
                except ValueError:
                    pass
                else:
                    if ndim is not None:
                        raise ValueError(
                            "Array should be defined with only "
                            "one string fixing the number of dimension. "
                            "Use for example NDim(2, 3)."
                        )
                    param = ndim = NDim(
                        tmp, name_calling_module=get_name_calling_module()
                    )

            if isinstance(param, str):
                if param == "memview":
                    memview = True
                    continue
                raise ValueError(f"{param} cannot be interpretted...")

            params_filtered.append(param)

        if dtype is None:
            raise ValueError("No way to determine the dtype of the array")

        if ndim is None:
            raise ValueError("No way to determine the ndim of the array")

        parameters = {p.__name__: p for p in params_filtered}

        ArrayBis = type(
            f"Array_{dtype.__name__}_{ndim}",
            (Array,),
            {"dtype": dtype, "ndim": ndim, "parameters": parameters},
        )
        ArrayBis.memview = memview

        return ArrayBis

    def get_parameters(self):
        return getattr(self, "parameters", dict())

    def get_template_parameters(self):
        return tuple(
            param
            for param in self.get_parameters().values()
            if isinstance(param, TemplateVar)
        )

    def __repr__(self):
        if not hasattr(self, "parameters"):
            return super().__repr__()

        strings = []
        for p in self.parameters.values():
            if isinstance(p, type):
                string = p.__name__
            else:
                string = repr(p)
            strings.append(string)

        if self.memview:
            strings.append('"memview"')

        return "Array[" + ", ".join(strings) + "]"

    def format_as_backend_type(self, backend_type_formatter, **kwargs):

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

        memview = kwargs.get("memview", self.memview)
        return backend_type_formatter.make_array_code(dtype, ndim, memview)


class Array(metaclass=ArrayMeta):
    """Represent a Numpy array in type hinname_calling_module"""

    pass


class UnionMeta(type):
    """Metaclass for the Union class"""

    def __getitem__(self, types):

        if not isinstance(types, tuple):
            types = (types,)

        name_calling_module = get_name_calling_module()
        template_var = UnionVar(*types, name_calling_module=name_calling_module)

        return type(
            "UnionBis", (Union,), {"types": types, "template_var": template_var}
        )

    def get_template_parameters(self):
        template_params = []
        for type_ in self.types:
            if hasattr(type_, "get_template_parameters"):
                template_params.extend(type_.get_template_parameters())

        template_params.append(self.template_var)

        return tuple(template_params)

    def __repr__(self):
        strings = []
        for p in self.types:
            if isinstance(p, type):
                string = p.__name__
            else:
                string = repr(p)
            strings.append(string)
        return "Union[" + ", ".join(strings) + "]"

    def format_as_backend_type(self, backend_type_formatter, **kwargs):
        type_ = kwargs.pop(self.template_var.__name__)
        return format_type_as_backend_type(
            type_, backend_type_formatter, **kwargs
        )


class Union(metaclass=UnionMeta):
    """Similar to typing.Union

    >>> U = Union[float, Array[int, "1d"]]

    """

    pass


class ListMeta(type):
    """Metaclass for the List class"""

    def __getitem__(self, type_):
        if isinstance(type_, str):
            type_ = str2type(type_)
        return type("ListBis", (List,), {"type_": type_})

    def get_template_parameters(self):
        if hasattr(self.type_, "get_template_parameters"):
            return self.type_.get_template_parameters()
        return tuple()

    def __repr__(self):
        if isinstance(self.type_, type):
            string = self.type_.__name__
        else:
            string = repr(self.type_)
        return f"List[{string}]"

    def format_as_backend_type(self, backend_type_formatter, **kwargs):
        return (
            format_type_as_backend_type(
                self.type_, backend_type_formatter, **kwargs
            )
            + " list"
        )


class List(metaclass=ListMeta):
    """Similar to typing.List

    >>> L = List[List[int]]

    """

    pass


class DictMeta(type):
    """Metaclass for the Dict class"""

    def __getitem__(self, types):
        type_keys, type_values = types
        if isinstance(type_keys, str):
            type_keys = str2type(type_keys)
        if isinstance(type_values, str):
            type_values = str2type(type_values)
        return type(
            "DictBis",
            (Dict,),
            {"type_keys": type_keys, "type_values": type_values},
        )

    def get_template_parameters(self):
        template_params = []
        if hasattr(self.type_keys, "get_template_parameters"):
            template_params.extend(self.type_keys.get_template_parameters())
        if hasattr(self.type_values, "get_template_parameters"):
            template_params.extend(self.type_values.get_template_parameters())
        return template_params

    def __repr__(self):
        if isinstance(self.type_keys, type):
            key = self.type_keys.__name__
        else:
            key = repr(self.type_keys)
        if isinstance(self.type_values, type):
            value = self.type_values.__name__
        else:
            value = repr(self.type_values)
        return f"Dict[{key}, {value}]"

    def format_as_backend_type(self, backend_type_formatter, **kwargs):
        key = format_type_as_backend_type(
            self.type_keys, backend_type_formatter, **kwargs
        )
        value = format_type_as_backend_type(
            self.type_values, backend_type_formatter, **kwargs
        )
        return backend_type_formatter.make_dict_code(key, value)


class Dict(metaclass=DictMeta):
    """Similar to typing.Dict

    >>> L = Dict[str, int]

    """

    pass


def format_type_as_backend_type(type_, backend_type_formatter, **kwargs):
    if isinstance(type_, str):
        type_ = str2type(type_)

    if hasattr(type_, "format_as_backend_type"):
        backend_type = type_.format_as_backend_type(
            backend_type_formatter, **kwargs
        )
    elif hasattr(type_, "__name__"):
        backend_type = type_.__name__
    else:
        print(type_)
        raise RuntimeError

    assert backend_type is not None

    return backend_type_formatter.normalize_type_name(backend_type)


def analyze_array_type(str_type):
    """Analyze an array type. return dtype, ndim"""
    dtype, end = str_type.split("[", 1)
    if not dtype.startswith("np."):
        dtype = "np." + dtype

    if ":" in end:
        ndim = end.count(":")
    else:
        ndim = end.count("[") + 1

    return dtype, ndim


def str2type(str_type):

    if " or " in str_type:
        subtypes = str_type.split(" or ")
        return Union[tuple(str2type(subtype) for subtype in subtypes)]

    try:
        return eval(str_type)
    except (TypeError, SyntaxError):
        # not a simple type
        pass

    words = [word for word in str_type.split(" ") if word]

    if words[-1] == "list":
        return List[" ".join(words[:-1])]

    if words[-1] == "dict":
        if len(words) != 3:
            print(words)
            raise NotImplementedError
        key = words[0][:-1]
        value = words[1]
        return Dict[key, value]

    dtype, ndim = analyze_array_type(str_type)

    dtype = eval(dtype, {"np": np})

    return Array[dtype, f"{ndim}d"]
