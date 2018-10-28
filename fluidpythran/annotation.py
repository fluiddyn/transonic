class TypeVar:
    def __init__(self, name):
        self.__name__ = name

    def get_pythran_type(self, **kwargs):

        dtype = None

        for key, value in kwargs.items():
            if key == self.__name__:
                dtype = value

        if dtype is None:
            raise ValueError

        return dtype.__name__


class DimVar:
    def __init__(self, name, shift=0):
        self.__name__ = name
        self.shift = shift

    def __repr__(self):
        return self.__name__

    def __add__(self, number):
        return type(self)(self.__name__, shift=number)

    def __sub__(self, number):
        return type(self)(self.__name__, shift=-number)


class ArrayMeta(type):
    def __getitem__(self, parameters):

        dtype = None
        ndim = None
        for param in parameters:
            if isinstance(param, TypeVar):
                if dtype is not None:
                    raise ValueError
            dtype = param

            if isinstance(param, DimVar):
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

    def __repr__(self):
        return "Array[" + ", ".join(repr(p) for p in self.parameters) + "]"

    def get_pythran_type(self, **kwargs):

        dtype = ndim = None

        for key, value in kwargs.items():
            try:
                template_var = self.parameters[key]
            except KeyError:
                continue

            if isinstance(template_var, TypeVar):
                dtype = value
            elif isinstance(template_var, DimVar):
                ndim = value + template_var.shift
            else:
                raise ValueError

        if dtype is None or ndim is None:
            raise ValueError

        return f"{dtype.__name__}[{', '.join([':']*ndim)}]"


class Array(metaclass=ArrayMeta):
    pass
