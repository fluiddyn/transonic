from tokenize import tokenize, untokenize, COMMENT, INDENT, DEDENT, STRING, NAME

from token import tok_name
from io import BytesIO

import inspect
from runpy import run_path

from pathlib import Path

import black


def parse_py(path):

    blocks = []
    signatures_blocks = {}
    code_blocks = {}

    functions = set()
    signatures_func = {}

    imports = []

    with open(path) as file:
        code = file.read()

    has_to_find_name_block = False
    has_to_find_signatures = False
    has_to_find_code_block = False
    in_def = False

    g = tokenize(BytesIO(code.encode("utf-8")).readline)
    for toknum, tokval, a, b, c in g:

        if (
            toknum == COMMENT
            and tokval.startswith("# pythran ")
            and "import" in tokval
        ):
            imports.append(tokval.split("# pythran ", 1)[1])

        if toknum == NAME and tokval == "use_pythranized_block":
            has_to_find_name_block = True
            has_to_find_signatures = True
            has_to_find_code_block = "after use_pythranized_block"

        if has_to_find_name_block and toknum == STRING:
            name_block = eval(tokval)
            has_to_find_name_block = False
            blocks.append(name_block)

        if toknum == COMMENT and tokval.startswith("# pythran def "):
            in_def = True
            signature_func = tokval.split("# pythran def ", 1)[1]
            name_func = signature_func.split("(")[0]
            functions.add(name_func)

            if name_func not in signatures_func:
                signatures_func[name_func] = []

            if ")" in tokval:
                in_def = False
                signatures_func[name_func].append(signature_func)

        if in_def:
            if toknum == COMMENT:
                signature_func += tokval
                if ")" in tokval:
                    in_def = False
                    signatures_func[name_func].append(signature_func)

        if has_to_find_signatures and toknum == COMMENT:
            if tokval.startswith("# pythran block "):
                in_signature = True
                signature = tokval.split("# pythran block ", 1)[1]
            elif in_signature:
                signature += tokval[1:].strip()
                if ")" in tokval and "-> (" not in tokval:
                    in_signature = False

                    if name_block not in signatures_blocks:
                        signatures_blocks[name_block] = []
                    signatures_blocks[name_block].append(signature)

        if has_to_find_code_block == "in block":
            code_blocks[name_block].append((toknum, tokval))

            if toknum == DEDENT:
                code_blocks[name_block] = untokenize(code_blocks[name_block])
                has_to_find_code_block = False

        if (
            has_to_find_code_block == "after use_pythranized_block"
            and toknum == INDENT
        ):
            has_to_find_code_block = "in block"
            code_blocks[name_block] = []

        # print((tok_name[toknum], tokval))

    return (
        blocks,
        signatures_blocks,
        code_blocks,
        functions,
        signatures_func,
        imports,
    )


def create_pythran_code(path_py):

    blocks, signatures_blocks, code_blocks, functions, signatures_func, imports = parse_py(
        path_py
    )

    print(signatures_blocks)

    code_pythran = "\n" + "\n".join(imports) + "\n"

    mod = run_path(path_py)
    for name_func in functions:
        signatures = signatures_func[name_func]
        for signature in signatures:
            code_pythran += f"# pythran export {signature}\n"

        func = mod[name_func]
        code = inspect.getsource(func)

        code_pythran += f"\n{code}\n\n"

    variables_types_block = {}
    return_block = {}
    for name_block, types_variables in signatures_blocks.items():
        variables_types_block[name_block] = []
        for types_variables1 in types_variables:
            variables_types = {}
            lines = types_variables1.split("(", 1)[1].split(")")[0].split(";")
            for line in lines:
                type_, *variables = line.split()
                for variable in variables:
                    variables_types[variable.replace(",", "")] = type_
            variables_types_block[name_block].append(variables_types)

        if types_variables and "->" in types_variables1:
            return_block[name_block] = types_variables1.split("->", 1)[1]

    # add "pythran export" for blocks
    for name_block, variables_types0 in variables_types_block.items():
        for variables_types in variables_types0:
            str_variables = ", ".join(variables_types.values())
            code_pythran += f"# pythran export {name_block}({str_variables})\n"

    arguments_blocks = {}

    # add code for blocks
    for name_block, variables_types0 in variables_types_block.items():
        variables = variables_types0[0].keys()
        arguments_blocks[name_block] = list(variables)

        str_variables = ", ".join(variables)

        code_pythran += f"def {name_block}({str_variables}):\n"

        code_block = code_blocks[name_block]

        code_pythran += 4 * " " + code_block.replace("\n", "\n" + 4 * " ") + "\n"

        if name_block in return_block:
            code_pythran += f"    return {return_block[name_block]}\n"

    code_pythran += "# pythran export arguments_blocks\n"

    code_pythran += "arguments_blocks = " + str(arguments_blocks)

    code_pythran = black.format_str(code_pythran, line_length=82)

    return code_pythran


def create_pythran_file(path_py):

    code_pythran = create_pythran_code(path_py)

    if not code_pythran:
        return

    print("code_pythran\n", code_pythran)

    path = Path(path_py)

    path_dir = path.parent / "_pythran"
    path_dir.mkdir(exist_ok=True)

    path_pythran = path_dir / ("_pythran_" + path.name)

    with open(path_pythran, "w") as file:
        file.write(code_pythran)

    print(f"File {str(path_pythran)} written")
