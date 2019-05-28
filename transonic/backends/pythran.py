"""Pythran Backend
==================


"""

from tokenize import tokenize, untokenize, NAME, OP
from io import BytesIO

# from token import tok_name
from textwrap import indent


try:
    import black
except ImportError:
    black = False

import transonic
from transonic.util import TypeHintRemover, format_str
from transonic.annotation import compute_pythran_types_from_valued_types

from transonic.analyses import analyse_aot
from transonic.analyses import extast


def get_code_function(fdef):

    transformed = TypeHintRemover().visit(fdef)
    # convert the AST back to source code
    code = extast.unparse(transformed)

    code = format_str(code)

    return code


def produce_new_code_method(fdef, class_def):

    src = get_code_function(fdef)

    tokens = []
    attributes = set()

    using_self = False

    g = tokenize(BytesIO(src.encode("utf-8")).readline)
    for toknum, tokval, a, b, c in g:
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

    func_name = fdef.name

    index_func_name = tokens.index((NAME, func_name))
    name_new_func = f"__for_method__{class_def.name}__{func_name}"
    tokens[index_func_name] = (NAME, name_new_func)

    new_code = untokenize(tokens).decode("utf-8")

    return new_code, attributes, name_new_func


def produce_code_for_method(
    fdef, class_def, annotations_meth, annotations_class, jit=False
):

    class_name = class_def.name
    meth_name = fdef.name

    new_code, attributes, name_new_func = produce_new_code_method(fdef, class_def)

    types_attrs = []

    for attr in attributes:
        if attr not in annotations_class:
            raise NotImplementedError(
                f"self.{attr} used but {attr} not in class annotations"
            )
    types_attrs = [annotations_class[attr] for attr in attributes]

    types_func = list(annotations_meth.values())

    types_pythran = types_attrs + types_func

    try:
        types_string_signatures = compute_pythran_types_from_valued_types(
            types_pythran
        )
    except ValueError:
        if jit:
            types_string_signatures = []
        else:
            raise

    pythran_signatures = set()

    for types_string_signature in types_string_signatures:
        pythran_signatures.add(
            "# pythran export "
            + name_new_func
            + "("
            + ", ".join(types_string_signature)
            + ")\n"
        )

    if jit:
        new_code = "from transonic import jit\n\n@jit\n" + new_code

    python_code = "\n".join(sorted(pythran_signatures)) + "\n" + new_code

    str_self_dot_attributes = ", ".join("self." + attr for attr in attributes)
    args_func = [arg.id for arg in fdef.args.args[1:]]
    str_args_func = ", ".join(args_func)

    defaults = fdef.args.defaults
    nb_defaults = len(defaults)
    nb_args = len(fdef.args.args)
    nb_no_defaults = nb_args - nb_defaults - 1

    str_args_value_func = []
    ind_default = 0
    for ind, arg in enumerate(fdef.args.args[1:]):
        name = arg.id
        if ind < nb_no_defaults:
            str_args_value_func.append(f"{name}")
        else:
            default = extast.unparse(defaults[ind_default]).strip()
            str_args_value_func.append(f"{name}={default}")
            ind_default += 1

    str_args_value_func = ", ".join(str_args_value_func)

    if jit:
        name_new_method = f"__new_method__{class_name}__{meth_name}"
        python_code += (
            f"\ndef {name_new_method}"
            f"(self, {str_args_value_func}):\n"
            f"    return {name_new_func}({str_self_dot_attributes}, {str_args_func})"
            "\n"
        )
    else:
        name_var_code_new_method = f"__code_new_method__{class_name}__{meth_name}"
        python_code += (
            f"\n# pythran export {name_var_code_new_method}\n"
            f'\n{name_var_code_new_method} = """\n\n'
            f"def new_method(self, {str_args_value_func}):\n"
            f"    return pythran_func({str_self_dot_attributes}, {str_args_func})"
            '\n\n"""\n'
        )

    python_code = format_str(python_code)

    return python_code


def make_pythran_code(path_py):
    """Create a pythran code from a Python file"""
    with open(path_py) as file:
        code_module = file.read()

    boosted_dicts, code_dependance, annotations, blocks = analyse_aot(code_module)

    code = ["\n" + code_dependance + "\n"]

    for func_name, fdef in boosted_dicts["functions"].items():

        signatures_func = set()

        try:
            ann = annotations["functions"][func_name]
        except KeyError:
            pass
        else:
            typess = compute_pythran_types_from_valued_types(ann.values())

            for types in typess:
                signatures_func.add(
                    f"# pythran export {func_name}({', '.join(types)})"
                )

        anns = annotations["comments"][func_name]

        for ann in anns:
            typess = compute_pythran_types_from_valued_types(ann.values())

            for types in typess:
                signatures_func.add(
                    f"# pythran export {func_name}({', '.join(types)})"
                )

        code.append("\n".join(sorted(signatures_func)))

        code.append(get_code_function(fdef))

    for (class_name, meth_name), fdef in boosted_dicts["methods"].items():

        class_def = boosted_dicts["classes"][class_name]

        if class_name in annotations["classes"]:
            annotations_class = annotations["classes"][class_name]
        else:
            annotations_class = {}

        if (class_name, meth_name) in annotations["methods"]:
            annotations_meth = annotations["methods"][(class_name, meth_name)]
        else:
            annotations_meth = {}

        code_for_meth = produce_code_for_method(
            fdef, class_def, annotations_meth, annotations_class
        )

        code.append(code_for_meth)

    for block in blocks:
        signatures_block = set()
        for ann in block.signatures:
            typess = compute_pythran_types_from_valued_types(ann.values())

            for types in typess:
                signatures_block.add(
                    f"# pythran export {block.name}({', '.join(types)})"
                )

        code.extend(sorted(signatures_block))

        str_variables = ", ".join(block.signatures[0].keys())

        code.append(f"\ndef {block.name}({str_variables}):\n")

        code_block = indent(extast.unparse(block.ast_code), "    ")

        code.append(code_block)

        if block.results:
            code.append(f"    return {', '.join(block.results)}\n")

    arguments_blocks = {
        block.name: list(block.signatures[0].keys()) for block in blocks
    }

    if arguments_blocks:
        code.append(
            "# pythran export arguments_blocks\n"
            f"arguments_blocks = {str(arguments_blocks)}\n"
        )

    code = "\n".join(code).strip()

    if code:
        code += (
            "\n\n# pythran export __transonic__\n"
            f"__transonic__ = ('{transonic.__version__}',)"
        )

    code = format_str(code)

    return code
