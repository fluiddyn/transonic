"""Make the Pythran files for the classes
=========================================

TODO: This code should be put in the backends...

"""

from tokenize import tokenize, untokenize, NAME, OP

from token import tok_name
import inspect
from io import BytesIO

from transonic.annotation import compute_pythran_types_from_valued_types
from transonic.log import logger
from transonic.util import get_source_without_decorator, format_str


def produce_code_class(cls, jit=False):
    pythran_code = ""
    for key, value in cls.__dict__.items():
        if hasattr(value, "__transonic__") and value.__transonic__ in (
            "trans_def_method",
            "jit_method",
        ):
            pythran_code += produce_code_class_func(cls, key, jit)
    return pythran_code


def produce_new_code_method(cls, func):

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
            elif toknum == OP and tokval in (",", ")"):
                tokens.append((NAME, "self"))
                using_self = False
            else:
                raise NotImplementedError(
                    f"self{tokval} not supported by Transonic"
                )

        if using_self == ".":
            if toknum == NAME:
                using_self = False
                tokens.append((NAME, "self_" + tokval))
                attributes.add(tokval)
                continue
            else:
                raise NotImplementedError

        if toknum == NAME and tokval == "self":
            using_self = "self"
            continue

        tokens.append((toknum, tokval))

    attributes = sorted(attributes)

    attributes_self = ["self_" + attr for attr in attributes]

    index_self = tokens.index((NAME, "self"))

    tokens_attr = []
    for ind, attr in enumerate(attributes_self):
        tokens_attr.append((NAME, attr))
        tokens_attr.append((OP, ","))

    if tokens[index_self + 1] == (OP, ","):
        del tokens[index_self + 1]

    tokens = tokens[:index_self] + tokens_attr + tokens[index_self + 1 :]

    index_func_name = tokens.index((NAME, func.__name__))
    cls_name = cls.__name__
    name_new_func = f"__for_method__{cls_name}__{func.__name__}"
    tokens[index_func_name] = (NAME, name_new_func)

    new_code = untokenize(tokens).decode("utf-8")

    return new_code, attributes, name_new_func


def produce_code_class_func(cls, func_name, jit=False):

    func = cls.__dict__[func_name]

    if jit:
        func = func.func

    new_code, attributes, name_new_func = produce_new_code_method(cls, func)

    try:
        cls_annotations = cls.__annotations__
    except AttributeError:
        cls_annotations = {}

    if jit:
        types_attrs = [
            cls_annotations[attr]
            for attr in attributes
            if attr in cls_annotations
        ]
    else:
        for attr in attributes:
            if attr not in cls_annotations:
                raise NotImplementedError(
                    f"self.{attr} used but {attr} not in class annotations"
                )
        types_attrs = [cls_annotations[attr] for attr in attributes]

    signature = inspect.signature(func)
    types_func = [param.annotation for param in signature.parameters.values()][1:]
    types_pythran = types_attrs + types_func

    pythran_signatures = "\n"

    try:
        types_string_signatures = compute_pythran_types_from_valued_types(
            types_pythran
        )
    except ValueError:
        if jit:
            types_string_signatures = []
        else:
            raise

    for types_string_signature in types_string_signatures:
        pythran_signatures += (
            "# pythran export "
            + name_new_func
            + "("
            + ", ".join(types_string_signature)
            + ")\n"
        )

    if jit:
        new_code = "from transonic import jit\n\n@jit\n" + new_code

    python_code = pythran_signatures + "\n" + new_code

    str_self_dot_attributes = ", ".join("self." + attr for attr in attributes)
    args_func = list(signature.parameters.keys())[1:]
    str_args_func = ", ".join(args_func)

    str_args_value_func = ""
    for param, value in signature.parameters.items():
        if param == "self":
            continue
        elif value.default is value.empty:
            str_args_value_func += f"{param}, "
        else:
            str_args_value_func += f"{param}={value.default}, "

    str_args_value_func = str_args_value_func.rstrip(", ")

    if jit:
        name_new_method = f"__new_method__{cls.__name__}__{func_name}"
        python_code += (
            f"\ndef {name_new_method}"
            f"(self, {str_args_value_func}):\n"
            f"    return {name_new_func}({str_self_dot_attributes}, {str_args_func})"
            "\n"
        )
    else:
        name_var_code_new_method = (
            f"__code_new_method__{cls.__name__}__{func_name}"
        )
        python_code += (
            f"\n# pythran export {name_var_code_new_method}\n"
            f'\n{name_var_code_new_method} = """\n\n'
            f"def new_method(self, {str_args_value_func}):\n"
            f"    return backend_func({str_self_dot_attributes}, {str_args_func})"
            '\n\n"""\n'
        )

    python_code = format_str(python_code)

    return python_code
