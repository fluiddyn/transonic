import ast
import astunparse


class TypeVar:
    def __init__(self, name):
        self.__name__ = name

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


class NDimVar:
    def __init__(self, name, shift=0):
        self.__name__ = name
        self.shift = shift

    def __repr__(self):

        name = self.__name__

        if self.shift < 0:
            name = name + f" - {abs(self.shift)}"
        elif self.shift > 0:
            name = name + f" + {abs(self.shift)}"

        return name

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

            if isinstance(param, NDimVar):
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
        return (
            "Array[" + ", ".join(repr(p) for p in self.parameters.values()) + "]"
        )

    def get_pythran_type(self, **kwargs):

        dtype = ndim = None

        for key, value in kwargs.items():
            try:
                template_var = self.parameters[key]
            except KeyError:
                continue

            if isinstance(template_var, TypeVar):
                dtype = value
            elif isinstance(template_var, NDimVar):
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
