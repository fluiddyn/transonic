from tokenize import tokenize, untokenize, NAME, OP
from token import tok_name
from io import BytesIO
import inspect

import numpy as np

from transonic.log import logger
from transonic.util import get_source_without_decorator, format_str
from transonic.annotation import compute_signatures_from_typeobjects


def trans_def_method(func):
    func.__transonic__ = "trans_def_method"
    return func


# logger.set_level("debug")


from transonic import Array, Type, NDim

A = Array[Type(float, int), NDim(1, 2)]


class Transmitter:
    freq: float

    def __init__(self):
        pass

    @trans_def_method
    def __call__(self, inp: A):
        """My docstring"""
        return inp * np.exp(np.arange(len(inp)) * self.freq * 1j)

    @trans_def_method
    def call_with_print(self, inp: A):
        """call + print"""
        print("call_with_print")
        return inp * np.exp(np.arange(len(inp)) * self.freq * 1j)


def produce_pythran_code_class(cls):

    pythran_code = ""

    for key, value in cls.__dict__.items():
        if (
            hasattr(value, "__transonic__")
            and value.__transonic__ == "trans_def_method"
        ):
            pythran_code += produce_pythran_code_class_func(cls, key)

    return pythran_code


def produce_pythran_code_class_func(cls, func_name):

    cls_name = cls.__name__
    cls_annotations = cls.__annotations__

    func = cls.__dict__[func_name]

    signature = inspect.signature(func)
    types_func = [param.annotation for param in signature.parameters.values()][1:]
    args_func = list(signature.parameters.keys())[1:]

    src = get_source_without_decorator(func)

    tokens = []
    attributes = set()

    using_self = False

    g = tokenize(BytesIO(src.encode("utf-8")).readline)
    for toknum, tokval, a, b, c in g:
        logger.debug((tok_name[toknum], tokval))

        if using_self == "self":
            if toknum == OP and tokval == ".":
                using_self = tokval
                continue
            elif toknum == OP and tokval == ",":
                tokens.append((NAME, "self"))
                using_self = False
            else:
                raise RuntimeError

        if using_self == ".":
            if toknum == NAME and tokval in cls_annotations:
                using_self = False
                tokens.append((NAME, "self_" + tokval))
                attributes.add(tokval)
                continue
            else:
                raise RuntimeError

        if toknum == NAME and tokval == "self":
            using_self = tokval
            continue

        tokens.append((toknum, tokval))

    attributes = sorted(attributes)

    types_attrs = [cls_annotations[attr] for attr in attributes]

    attributes_self = ["self_" + attr for attr in attributes]

    index_self = tokens.index((NAME, "self"))

    tokens_attr = []
    for ind, attr in enumerate(attributes_self):
        tokens_attr.append((NAME, attr))
        tokens_attr.append((OP, ","))

    tokens = tokens[:index_self] + tokens_attr + tokens[index_self + 2 :]

    index_func_name = tokens.index((NAME, func_name))
    name_backend_func = f"__for_method__{cls_name}__{func_name}"
    tokens[index_func_name] = (NAME, name_backend_func)

    new_code = untokenize(tokens).decode("utf-8")
    new_code = format_str(new_code)

    # args_pythran = attributes + args_func
    types_pythran = types_attrs + types_func

    pythran_signatures = "\n"

    for types_string_signature in compute_signatures_from_typeobjects(
        types_pythran
    ):
        pythran_signatures += (
            "# pythran export "
            + name_backend_func
            + "("
            + ", ".join(types_string_signature)
            + ")\n"
        )

    pythran_code = pythran_signatures + "\n" + new_code

    name_var_code_new_method = f"__code_new_method__{cls_name}__{func_name}"

    str_self_dot_attributes = ", ".join("self." + attr for attr in attributes)
    str_args_func = ", ".join(args_func)

    pythran_code += (
        f"\n# pythran export {name_var_code_new_method}\n"
        f'\n{name_var_code_new_method} = """\n\n'
        f"def new_method(self, {str_args_func}):\n"
        f"    return backend_func({str_self_dot_attributes}, {str_args_func})"
        '\n\n"""\n'
    )

    return pythran_code


pythran_code = produce_pythran_code_class(Transmitter)
print(pythran_code)
