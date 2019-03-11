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

.. autoclass:: Shape
   :members:
   :private-members:

.. autoclass:: Array
   :members:
   :private-members:

.. autoclass:: Union
   :members:
   :private-members:

Internal API
------------

.. autoclass:: TemplateVar
   :members:
   :private-members:

.. autoclass:: ArrayMeta
   :members:
   :private-members:

.. autofunction:: compute_pythran_types_from_types

.. autofunction:: compute_pythran_types_from_valued_types

.. autofunction:: make_signature_from_template_variables

.. autofunction:: make_signatures_from_typehinted_func

"""

import itertools
import inspect

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


class Shape(TemplateVar):
    """Shape template variable

    NotImplemented!

    """

    _letter = "S"
    _type_values = str, list, tuple

    def _is_correct_for_name(self, arg):
        raise NotImplementedError
        return isinstance(arg, str)


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
                raise ValueError(f"{param} cannot be interpretted...")

            params_filtered.append(param)

        if dtype is None:
            raise ValueError("No way to determine the dtype of the array")

        if ndim is None:
            raise ValueError("No way to determine the ndim of the array")

        parameters = {p.__name__: p for p in params_filtered}

        ArrayBis = type(
            "ArrayBis",
            (Array,),
            {"dtype": dtype, "ndim": ndim, "parameters": parameters},
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

        base = f"{dtype.__name__}"
        if ndim == 0:
            return base
        return base + f"[{', '.join([':']*ndim)}]"


class Array(metaclass=ArrayMeta):
    """Represent a Numpy array in type hinname_calling_module"""

    pass


class UnionMeta(type):
    """Metaclass for the Array class used for type hinname_calling_module"""

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

    def get_pythran_type(self, **kwargs):
        type_ = kwargs.pop(self.template_var.__name__)
        return compute_pythran_type_from_type(type_, **kwargs)


class Union(metaclass=UnionMeta):
    """Similar to typing.Union

    >>> U = Union[float, Array[int, "1d"]]

    """

    pass


normalized_types = {"float": "float64", "complex": "complex128"}


def normalize_type_name(name):
    try:
        return normalized_types[name]
    except KeyError:
        return name


def compute_pythran_type_from_type(type_, **kwargs):
    if hasattr(type_, "get_pythran_type"):
        pythran_type = type_.get_pythran_type(**kwargs)
    elif hasattr(type_, "__name__"):
        pythran_type = type_.__name__
    else:
        pythran_type = str(type_)
        types = pythran_type.split(" or ")
        new_types = []
        for _type in types:
            _type = normalize_type_name(_type)
            if "][" in _type:
                # C style: we try to rewrite it in Cython style
                base, dims = _type.split("[", 1)
                dims = ", ".join([_ or ":" for _ in dims[:-1].split("][")])
                _type = normalize_type_name(base) + "[" + dims + "]"
            elif _type.endswith("[]"):
                _type = normalize_type_name(_type[:-2]) + "[:]"
            new_types.append(_type)
        pythran_type = " or ".join(new_types)

    return normalize_type_name(pythran_type)


def compute_pythran_types_from_types(types, **kwargs):
    """Compute a list of pythran types

    """
    pythran_types = []
    for type_ in types:
        pythran_types.append(compute_pythran_type_from_type(type_, **kwargs))

        if "_empty" in pythran_types:
            raise ValueError(
                "At least one annotation type lacking in a signature.\n"
                f"types = {types}"
            )

    return pythran_types


def compute_pythran_types_from_valued_types(types):
    """Compute a list of pythran types

    """
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

        if "_empty" in str_types:
            raise ValueError(
                "At least one annotation type lacking in a signature.\n"
                f"types = {types}"
            )

        return (str_types,)

    if not all(param.values for param in template_parameters):
        raise ValueError(
            f"{template_parameters}, {[param.values for param in template_parameters]}"
        )

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


def make_signature_from_template_variables(func, _signature=None, **kwargs):
    """Create signature for a function with values for the template types

    Parameters
    ----------

    func: a function

    kwargs : dict

        The template types and their value

    """
    if _signature is None:
        _signature = inspect.signature(func)

    types = [param.annotation for param in _signature.parameters.values()]

    pythran_types = compute_pythran_types_from_types(types, **kwargs)

    # "multiply" the signatures to take into account the "or" syntax
    multi_pythran_types = [
        _ for _ in itertools.product(*[t.split(" or ") for t in pythran_types])
    ]
    signatures = []
    for pythran_types in multi_pythran_types:
        signatures.append(f"{func.__name__}(" + ", ".join(pythran_types) + ")")

    return signatures


def make_signatures_from_typehinted_func(func):
    """Make the signatures from annotations if it is possible

    Useful when there are only "not templated" types.

    """
    annotations = func.__annotations__

    if not annotations:
        return tuple()

    types = annotations.values()

    template_parameters = []

    for type_ in types:
        if hasattr(type_, "get_template_parameters"):
            template_parameters.extend(type_.get_template_parameters())

    template_parameters = set(template_parameters)

    _signature = inspect.signature(func)

    if not template_parameters:
        signatures = make_signature_from_template_variables(
            func, _signature=_signature
        )
        return signatures

    if not all(param.values for param in template_parameters):
        return tuple()

    values_template_parameters = {}
    for param in template_parameters:
        values_template_parameters[param.__name__] = param.values

    names = values_template_parameters.keys()
    signatures = []
    for set_types in itertools.product(*values_template_parameters.values()):
        template_variables = {
            name: value for name, value in zip(names, set_types)
        }
        signatures.extend(
            make_signature_from_template_variables(
                func, _signature=_signature, **template_variables
            )
        )

    return signatures
