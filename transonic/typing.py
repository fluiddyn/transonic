"""Create Pythran signatures from type hints
============================================

User API
--------

.. autoclass:: Type
   :members:

.. autoclass:: NDim
   :members:

.. autoclass:: Array
   :members:
   :private-members:

.. autoclass:: List
   :members:
   :private-members:

.. autoclass:: Tuple
   :members:
   :private-members:

.. autoclass:: Dict
   :members:
   :private-members:

.. autoclass:: Set
   :members:
   :private-members:

.. autoclass:: Union
   :members:
   :private-members:

.. autofunction:: str2type

.. autofunction:: typeof

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
import re
from enum import Enum, auto

import numpy as np

from transonic.util import get_name_calling_module

names_template_variables = {}


class TemplateVar:
    """Base class for template variables

    >>> T = TemplateVar("T")
    >>> T = TemplateVar("T", int, float)

    >>> T = TemplateVar()
    Traceback (most recent call last):
        ...
    ValueError

    >>> T = TemplateVar(1)
    Traceback (most recent call last):
        ...
    TypeError: (1,) [False]
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
    """Template variable representing the dtype of an array.

    As a user, it is useful only for fused types.

    >>> T = Type(int, float)
    """

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
    """Template variable representing the number of dimension of an array.

    As a user, it is useful only for fused types.

    >>> N = NDim(1, 2)
    >>> N1 = N + 1

    """

    _type_values = int
    _letter = "N"

    def __init__(self, *args, shift=0, name_calling_module=None):

        if name_calling_module is None:
            name_calling_module = get_name_calling_module()

        super().__init__(*args, name_calling_module=name_calling_module)
        self.shift = shift

    def __repr__(self):

        if len(self.values) == 1 and self.shift == 0:
            return f'"{self.values[0]}d"'

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
    """TemplateVar used for the Union type"""

    _type_values = (type, type(None))
    _letter = "U"


class Meta(type):
    """Type of the Transonic types (used to create metaclasses)"""

    def __call__(cls, *args, **kwargs):
        raise RuntimeError("Transonic types are not meant to be instantiated")


class MemLayout(Enum):
    C = auto()
    F = auto()
    C_or_F = auto()
    strided = auto()

    def __repr__(self):
        return f'"{self.name}"'


def str2shape(str_shape):
    assert str_shape.startswith("[") and str_shape.endswith("]")
    str_shape = str_shape.replace(" ", "")
    if str_shape == "[]":
        return (None,)
    n = str_shape.count("]")
    if n > 1:
        return (None,) * n
    shape = []
    for symbol in str_shape[1:-1].split(","):
        if symbol == ":":
            value = None
        elif symbol == "":
            continue
        else:
            value = int(symbol)
        shape.append(value)
    return tuple(shape)


def shape2str(shape):
    symbols = [":" if value is None else str(value) for value in shape]
    tmp = ",".join(symbols)
    return f'"[{tmp}]"'


class ArrayMeta(Meta):
    """Metaclass for the Array class"""

    def __getitem__(self, parameters):

        if not isinstance(parameters, tuple):
            parameters = (parameters,)

        dtype = None
        ndim = None
        memview = False
        mem_layout = MemLayout.C_or_F
        shape = None
        params_filtered = []
        for param in parameters:
            if param is None:
                continue
            if isinstance(param, (Type, type, np.dtype)):
                if dtype is not None:
                    raise ValueError(
                        "Array should be defined with only one variable defining "
                        "the types. For more than one type, use "
                        "for example Type(float, int)"
                    )
                if isinstance(param, np.dtype):
                    param = param.type

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
                param = param.strip()
                if param == "memview":
                    memview = True
                    continue
                if param.startswith("[") and param.endswith("]"):
                    shape = str2shape(param)
                    continue
                try:
                    mem_layout = MemLayout[param]
                    continue
                except KeyError:
                    pass
                raise ValueError(f"{param} cannot be interpretted...")

            params_filtered.append(param)

        if shape is not None:
            if ndim is None:
                ndim = NDim(
                    len(shape), name_calling_module=get_name_calling_module()
                )
                params_filtered.append(ndim)
            elif ndim != len(shape):
                raise ValueError("ndim != len(shape)")
            if not any(shape):
                shape = None

        if dtype is None:
            raise ValueError("No way to determine the dtype of the array")

        if ndim is None:
            raise ValueError("No way to determine the ndim of the array")

        parameters = {p.__name__: p for p in params_filtered}

        ArrayBis = type(
            f"Array_{dtype.__name__}_{ndim}",
            (Array,),
            {
                "dtype": dtype,
                "ndim": ndim,
                "parameters": parameters,
                "memview": memview,
                "mem_layout": mem_layout,
                "shape": shape,
            },
        )
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

        if self.shape is not None:
            parameters = [
                param
                for param in self.parameters.values()
                if not isinstance(param, NDim)
            ]
        else:
            parameters = self.parameters.values()

        strings = []
        for p in parameters:
            if isinstance(p, type):
                string = p.__name__
            else:
                string = repr(p)
            strings.append(string)

        if self.shape is not None:
            strings.append(shape2str(self.shape))

        if self.memview:
            strings.append('"memview"')

        if self.mem_layout is not MemLayout.C_or_F:
            strings.append(repr(self.mem_layout))

        return f"Array[{', '.join(strings)}]"

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
        return backend_type_formatter.make_array_code(
            dtype, ndim, self.shape, memview, self.mem_layout
        )


class Array(metaclass=ArrayMeta):
    """Represent a Numpy array.

    >>> Array[int, "2d"]
    Array[int, "2d"]

    >>> Array[int, "2d", "C"]
    Array[int, "2d", "C"]

    >>> Array[int, "2d", "F"]
    Array[int, "2d", "F"]

    >>> Array[int, "2d", "strided"]
    Array[int, "2d", "strided"]

    Fused types:

    >>> Array[Type(int, float), "1d"]
    Array[T0, "1d"]

    >>> Array[float, NDim(2, 3)]
    Array[float, N5]

    """


class UnionMeta(Meta):
    """Metaclass for the Union class"""

    def __getitem__(self, types):

        types_in = types
        if not isinstance(types_in, tuple):
            types_in = (types_in,)

        types = []
        for type_ in types_in:
            if isinstance(type_, str):
                type_ = str2type(type_)
            types.append(type_)
        types = tuple(types)

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


class ListMeta(Meta):
    """Metaclass for the List class"""

    def __getitem__(self, type_elem):
        if isinstance(type_elem, str):
            type_elem = str2type(type_elem)
        return type("ListBis", (List,), {"type_elem": type_elem})

    def get_template_parameters(self):
        if hasattr(self.type_elem, "get_template_parameters"):
            return self.type_elem.get_template_parameters()
        return tuple()

    def __repr__(self):
        if isinstance(self.type_elem, type):
            string = self.type_elem.__name__
        else:
            string = repr(self.type_elem)
        return f"List[{string}]"

    def format_as_backend_type(self, backend_type_formatter, **kwargs):
        return backend_type_formatter.make_list_code(self.type_elem, **kwargs)


class List(metaclass=ListMeta):
    """Similar to typing.List

    >>> L = List[List[int]]

    """


class DictMeta(Meta):
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
        return backend_type_formatter.make_dict_code(
            self.type_keys, self.type_values, **kwargs
        )


class Dict(metaclass=DictMeta):
    """Similar to typing.Dict

    >>> L = Dict[str, int]

    """


class SetMeta(Meta):
    """Metaclass for the Set class"""

    def __getitem__(self, type_keys):
        if isinstance(type_keys, str):
            type_keys = str2type(type_keys)
        return type("SetBis", (Set,), {"type_keys": type_keys})

    def get_template_parameters(self):
        if hasattr(self.type_keys, "get_template_parameters"):
            return self.type_keys.get_template_parameters()
        else:
            return tuple()

    def __repr__(self):
        if isinstance(self.type_keys, type):
            key = self.type_keys.__name__
        else:
            key = repr(self.type_keys)
        return f"Set[{key}]"

    def format_as_backend_type(self, backend_type_formatter, **kwargs):
        return backend_type_formatter.make_set_code(self.type_keys, **kwargs)


class Set(metaclass=SetMeta):
    """Similar to typing.Set

    >>> S = Set[str]

    """


class TupleMeta(Meta):
    """Metaclass for the Tuple class"""

    def __getitem__(self, types):

        if not isinstance(types, tuple):
            types = (types,)

        trans_types = []
        for type_in in types:
            if isinstance(type_in, str):
                type_in(str2type(type_in))
            trans_types.append(type_in)

        return type("TupleBis", (Tuple,), {"types": trans_types})

    def get_template_parameters(self):
        template_params = []
        for type_ in self.types:
            if hasattr(type_, "get_template_parameters"):
                template_params.extend(type_.get_template_parameters())
        return tuple(template_params)

    def __repr__(self):
        strings = []
        for type_ in self.types:
            if isinstance(type_, Meta):
                name = repr(type_)
            elif isinstance(type_, type):
                name = type_.__name__
            else:
                name = repr(type_)
            strings.append(name)
        return f"Tuple[{', '.join(strings)}]"

    def format_as_backend_type(self, backend_type_formatter, **kwargs):
        return backend_type_formatter.make_tuple_code(self.types, **kwargs)


class Tuple(metaclass=TupleMeta):
    """Similar to typing.Tuple

    >>> T = Tuple[int, Array[int, "2d"]]

    """


class OptionalMeta(Meta):
    def __getitem__(self, type_):
        return Union[type_, None]


class Optional(metaclass=OptionalMeta):
    """Similar to typing.Optional

    >>> Optional[int]
    Union[int, None]

    """


def format_type_as_backend_type(type_, backend_type_formatter, **kwargs):
    """Format a Transonic type as a backend (Pythran, Cython, ...) type

    """
    if type_ is None:
        # None has a special meaning for typing...
        return "None"

    if isinstance(type_, str):
        type_ = str2type(type_)

    if hasattr(type_, "format_as_backend_type"):
        backend_type = type_.format_as_backend_type(
            backend_type_formatter, **kwargs
        )
    elif hasattr(type_, "__name__"):
        backend_type = type_.__name__
    else:
        raise RuntimeError(f"type_: {type_}")

    assert backend_type is not None

    return backend_type_formatter.normalize_type_name(backend_type)


def str2type(str_type):
    """Compute a Transonic type from a string

    >>> str2type("int[:,:]")
    Array[int, "2d"]

    >>> str2type("int or float[]")
    Union[int, Array_float_"1d"]

    >>> str2type("(int, float[:, :])")
    Tuple[int, Array[float, "2d"]]
    """

    str_type = str_type.strip()

    if " or " in str_type:
        subtypes = str_type.split(" or ")
        return Union[tuple(str2type(subtype) for subtype in subtypes)]

    try:
        return eval(str_type)
    except (TypeError, SyntaxError, NameError):
        # not a simple type
        pass

    # could be a numpy type
    try:
        if not str_type.startswith("np."):
            dtype = "np." + str_type
        else:
            dtype = str_type
        return eval(dtype, {"np": np})
    except (TypeError, SyntaxError, AttributeError):
        pass

    if str_type.startswith("(") and str_type.endswith(")"):
        re_comma = re.compile(r",(?![^\[]*\])(?![^\(]*\))")
        return Tuple[
            tuple(
                str2type(word) for word in re_comma.split(str_type[1:-1]) if word
            )
        ]

    words = [word for word in str_type.split(" ") if word]

    if words[-1] == "list":
        return List[" ".join(words[:-1])]

    if words[-1] == "dict":
        if len(words) != 3:
            raise NotImplementedError(f"words: {words}")
        key = words[0][:-1]
        value = words[1]
        return Dict[key, value]

    if words[-1] == "set":
        if len(words) != 2:
            raise NotImplementedError(f"words: {words}")
        key = words[0]
        return Set[key]

    # str_type should be of the form "int[]"
    if "[" not in str_type:
        raise ValueError(f"Can't determine the Transonic type from '{str_type}'")

    dtype, str_shape = str_type.split("[", 1)
    if not dtype.startswith("np."):
        dtype = "np." + dtype
    str_shape = "[" + str_shape
    dtype = eval(dtype, {"np": np})
    return Array[dtype, str_shape]


_simple_types = (int, float, complex, str)


def typeof(obj):
    """Compute the Transonic type corresponding to a Python object

    Supports:

    - simple Python types (int, float, complex, str)
    - homogeneous list, dict and set
    - tuple
    - numpy scalars
    - numpy arrays

    """
    if isinstance(obj, _simple_types):
        return type(obj)

    if isinstance(obj, tuple):
        return Tuple[tuple(typeof(elem) for elem in obj)]

    if isinstance(obj, (list, dict, set)) and not obj:
        raise ValueError(
            f"Cannot determine the full type of an empty {type(obj)}"
        )

    if isinstance(obj, list):

        type_elem = type(obj[0])
        if not all(isinstance(elem, type_elem) for elem in obj):
            raise ValueError("The list {obj} is not homogeneous in type")

        return List[typeof(obj[0])]

    if isinstance(obj, (dict, set)):
        key = next(iter(obj))
        type_key = type(key)
        if not all(isinstance(key, type_key) for key in obj):
            raise ValueError("The dict {obj} is not homogeneous in type")

        if isinstance(obj, dict):
            value = next(iter(obj.values()))
            type_value = type(value)
            if not all(isinstance(value, type_value) for value in obj.values()):
                raise ValueError("The dict {obj} is not homogeneous in type")
            return Dict[typeof(key), typeof(value)]
        else:
            return Set[typeof(key)]

    # TODO: Tuple
    if isinstance(obj, tuple):
        raise NotImplementedError

    if isinstance(obj, np.ndarray):
        if np.isscalar(obj):
            return obj.dtype.type

        # TODO: deeper analysis
        return Array[obj.dtype, f"{obj.ndim}d"]

    raise NotImplementedError(
        f"Not able to determine the full type of {obj} (of type {type(obj)})"
    )
