"""Make the Pythran files for the classes
=========================================

"""

from tokenize import tokenize, untokenize, NAME, OP

# from token import tok_name
import inspect
from io import BytesIO

from transonic.signatures import compute_signatures_from_typeobjects

# from transonic.log import logger
from transonic.util import (
    get_source_without_decorator,
    format_str,
    make_code_from_fdef_node,
)

from .typing import base_type_formatter


def produce_code_class(cls):
    pythran_code = ""
    for key, value in list(cls.__dict__.items()):
        if hasattr(value, "__transonic__") and value.__transonic__ in (
            "trans_def_method",
            "jit_method",
        ):
            pythran_code += make_code_method_jit(cls, key)
    return pythran_code


def make_code_method_jit(cls, func_name):

    func = cls.__dict__[func_name]
    func = func.func

    new_code, attributes, name_new_func = make_new_code_method_from_objects(
        cls, func
    )

    try:
        cls_annotations = cls.__annotations__
    except AttributeError:
        cls_annotations = {}

    types_attrs = [
        cls_annotations[attr] for attr in attributes if attr in cls_annotations
    ]

    signature = inspect.signature(func)
    types_func = [param.annotation for param in signature.parameters.values()][1:]
    types_pythran = types_attrs + types_func

    transonic_signatures = "\n"

    try:
        signatures_as_lists_strings = compute_signatures_from_typeobjects(
            types_pythran, base_type_formatter
        )
    except ValueError:
        signatures_as_lists_strings = []

    for signature_as_strings in signatures_as_lists_strings:
        transonic_signatures += (
            f"# transonic def {name_new_func}("
            + ", ".join(signature_as_strings)
            + ")\n"
        )

    new_code = "from transonic import jit\n\n@jit\n" + new_code

    python_code = transonic_signatures + "\n" + new_code

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

    name_new_method = f"__new_method__{cls.__name__}__{func_name}"
    python_code += (
        f"\ndef {name_new_method}"
        f"(self, {str_args_value_func}):\n"
        f"    return {name_new_func}({str_self_dot_attributes}, {str_args_func})"
        "\n"
    )

    python_code = format_str(python_code)

    return python_code


def make_new_code_method_from_nodes(class_def, fdef):
    source = make_code_from_fdef_node(fdef)
    return make_new_code_method_from_source(source, fdef.name, class_def.name)


def make_new_code_method_from_objects(cls, func):
    source = get_source_without_decorator(func)
    return make_new_code_method_from_source(source, func.__name__, cls.__name__)


def make_new_code_method_from_source(source, func_name, cls_name):

    tokens = []
    attributes = set()

    using_self = False

    g = tokenize(BytesIO(source.encode("utf-8")).readline)
    for toknum, tokval, _, _, _ in g:
        # logger.debug((tok_name[toknum], tokval))

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

    index_func_name = tokens.index((NAME, func_name))
    name_new_func = f"__for_method__{cls_name}__{func_name}"
    tokens[index_func_name] = (NAME, name_new_func)
    # change recursive calls
    if func_name in attributes:
        attributes.remove(func_name)
        index_rec_calls = [
            index
            for index, (name, value) in enumerate(tokens)
            if value == "self_" + func_name
        ]
        # delete the occurrence of "self_" + func_name in function parameter
        del tokens[index_rec_calls[0] + 1]
        del tokens[index_rec_calls[0]]
        # consider the two deletes
        offset = -2
        # adapt all recurrence calls
        for ind in index_rec_calls[1:]:
            # adapt the index to the inserts and deletes
            ind += offset
            tokens[ind] = (tokens[ind][0], name_new_func)
            # put the attributes in parameter
            for attr in reversed(attributes):
                tokens.insert(ind + 2, (1, ","))
                tokens.insert(ind + 2, (1, "self_" + attr))
            # consider the inserts
            offset += len(attributes) * 2
    new_code = untokenize(tokens).decode("utf-8")

    return new_code, attributes, name_new_func
