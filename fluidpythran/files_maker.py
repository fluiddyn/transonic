from tokenize import tokenize, untokenize, COMMENT, INDENT, DEDENT, STRING, NAME

import os
from datetime import datetime
from logging import DEBUG

from token import tok_name
from io import BytesIO
from pathlib import Path
from runpy import run_path

try:
    import black
except ImportError:
    black = False

from .log import logger, set_log_level
import fluidpythran


def parse_py(path):
    """Parse a .py file and return data"""

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
                if ")" in tokval and "-> (" not in tokval or tokval.endswith(")"):
                    in_signature = False

                    if name_block not in signatures_blocks:
                        signatures_blocks[name_block] = []
                    signatures_blocks[name_block].append(signature)

        if has_to_find_code_block == "in block":

            if toknum == DEDENT:
                logger.debug(
                    f"code_blocks[name_block]: {code_blocks[name_block]}"
                )

                code_blocks[name_block] = untokenize(code_blocks[name_block])
                has_to_find_code_block = False
            else:
                code_blocks[name_block].append((toknum, tokval))

        if (
            has_to_find_code_block == "after use_pythranized_block"
            and toknum == INDENT
        ):
            has_to_find_code_block = "in block"
            code_blocks[name_block] = []

        logger.debug((tok_name[toknum], tokval))

    if "make_signature(" in code:

        fluidpythran.is_compiling = True
        namespace = run_path(str(path))
        fluidpythran.is_compiling = False


    return (
        blocks,
        signatures_blocks,
        code_blocks,
        functions,
        signatures_func,
        imports,
    )


def get_code_functions(path_py, func_names):
    """Get the code of function from a path and function names"""

    with open(path_py) as file:
        code = file.read()

    indent = 0
    in_def = False
    codes = {}

    g = tokenize(BytesIO(code.encode("utf-8")).readline)
    for toknum, tokval, a, b, c in g:

        if toknum == INDENT:
            indent += 1

        if toknum == DEDENT:
            indent -= 1

        if in_def == "def" and tokval in func_names:
            in_def = tokval
            codes[in_def] = [(NAME, "def")]

        if indent == 0 and toknum == NAME and tokval == "def":
            in_def = "def"

        if in_def and in_def != "def":

            if indent == 0 and toknum == DEDENT:
                codes[in_def] = untokenize(codes[in_def])
                in_def = False
            else:
                codes[in_def].append((toknum, tokval))

        logger.debug((indent, tok_name[toknum], tokval))

    return codes


def make_pythran_code(path_py):
    """Create a pythran code from a Python file"""

    blocks, signatures_blocks, code_blocks, functions, signatures_func, imports = parse_py(
        path_py
    )

    if logger.isEnabledFor(DEBUG):
        logger.debug(
            f"""
blocks: {blocks}\n
signatures_blocks: {signatures_blocks}\n
code_blocks:  {code_blocks}\n
functions: {functions}\n
signatures_func: {signatures_func}\n
imports: {imports}\n"""
        )

    code_pythran = "\n" + "\n".join(imports) + "\n"

    codes_functions = get_code_functions(path_py, functions)

    for name_func in functions:
        signatures = signatures_func[name_func]
        for signature in signatures:
            code_pythran += f"# pythran export {signature}\n"

        code = codes_functions[name_func]

        code_pythran += f"\n{code}\n\n"

    variables_types_block = {}
    return_block = {}
    for name_block, types_variables in signatures_blocks.items():
        variables_types_block[name_block] = []
        for types_variables1 in types_variables:
            variables_types = {}
            lines = types_variables1.split("(", 1)[1].split(")")[0].split(";")
            for line in lines:
                type_, str_variables = line.split(" ", 1)
                variables = str_variables.split(",")
                for variable in variables:
                    variables_types[variable.replace(",", "").strip()] = type_
            variables_types_block[name_block].append(variables_types)

        if types_variables and "->" in types_variables1:
            return_block[name_block] = types_variables1.split("->", 1)[1]

    arguments_blocks = {}

    # add code for blocks
    for name_block, variables_types0 in variables_types_block.items():
        # add "pythran export" for blocks
        for variables_types in variables_types0:
            str_variables = ", ".join(variables_types.values())
            code_pythran += f"# pythran export {name_block}({str_variables})\n\n"

        # add code for blocks
        variables = variables_types0[0].keys()
        arguments_blocks[name_block] = list(variables)

        str_variables = ", ".join(variables)

        code_pythran += f"def {name_block}({str_variables}):\n"

        code_block = code_blocks[name_block]

        code_pythran += 4 * " " + code_block.replace("\n", "\n" + 4 * " ") + "\n"

        if name_block in return_block:
            code_pythran += f"    return {return_block[name_block]}\n"

    if arguments_blocks:
        code_pythran += "# pythran export arguments_blocks\n"
        code_pythran += "arguments_blocks = " + str(arguments_blocks)

    if black:
        code_pythran = black.format_str(code_pythran, line_length=82)

    return code_pythran


def modification_date(filename):
    """Get the modification date of a file"""
    t = os.path.getmtime(filename)
    return datetime.fromtimestamp(t)


def has_to_build(output_file, input_file):
    """Check if a file has to be (re)built"""
    if not output_file.exists():
        return True
    mod_date_output = modification_date(output_file)
    if mod_date_output < modification_date(input_file):
        return True
    return False


def make_pythran_file(path_py, force=False, log_level=None):
    """Create a Python file from a Python file (if necessary)"""
    if log_level is not None:
        set_log_level(log_level)

    path_py = Path(path_py)

    if path_py.absolute().parent.name == "_pythran":
        logger.debug(f"skip file {path_py}")
        return
    if not path_py.name.endswith(".py"):
        raise ValueError(
            "fluidpythran only processes Python file. Cannot process {path_py}"
        )

    path_dir = path_py.parent / "_pythran"
    path_pythran = path_dir / ("_" + path_py.name)

    if not has_to_build(path_pythran, path_py) and not force:
        logger.info(f"File {path_pythran} already up-to-date.")
        return

    code_pythran = make_pythran_code(path_py)

    if not code_pythran:
        return

    if path_pythran.exists() and not force:
        with open(path_pythran) as file:
            code_pythran_old = file.read()

        if code_pythran_old == code_pythran:
            logger.info(f"Code in file {path_pythran} already up-to-date.")
            return

    logger.debug(f"code_pythran:\n{code_pythran}")

    path_dir.mkdir(exist_ok=True)

    with open(path_pythran, "w") as file:
        file.write(code_pythran)

    logger.info(f"File {str(path_pythran)} written")

    return path_pythran


def make_pythran_files(paths, force=False, log_level=None):
    """Create Pythran files from a list of Python files"""

    if log_level is not None:
        set_log_level(log_level)

    paths_out = []
    for path in paths:
        path_out = make_pythran_file(path, force=force)
        if path_out:
            paths_out.append(path_out)

    if paths_out:
        nb_files = len(paths_out)
        if nb_files == 1:
            conjug = "s"
        else:
            conjug = ""

        logger.warning(
            f"{nb_files} files created or updated need{conjug}"
            " to be pythranized"
        )
