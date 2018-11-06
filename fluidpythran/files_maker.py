from tokenize import tokenize, untokenize, COMMENT, INDENT, DEDENT, STRING, NAME

import os
from datetime import datetime
from logging import DEBUG

from token import tok_name
from io import BytesIO
from pathlib import Path
from runpy import run_module, run_path
import inspect

try:
    import black
except ImportError:
    black = False

from .log import logger, set_log_level
from .annotation import strip_typehints, compute_pythran_types_from_valued_types
import fluidpythran


def parse_py_code(code):
    """Parse a .py file and return data"""

    blocks = []
    signatures_blocks = {}
    code_blocks = {}

    functions = set()
    signatures_func = {}

    imports = []

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

    return (
        blocks,
        signatures_blocks,
        code_blocks,
        functions,
        signatures_func,
        imports,
    )


def get_code_functions(code, func_names):
    """Get the code of function from a path and function names"""

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


def get_codes_from_functions(functions):

    codes = {}

    for name, func in functions.items():
        code = inspect.getsource(func)
        # remove the first line (should be the pythran_def decorator)
        code = code.split("\n", 1)[1]
        code = strip_typehints(code)
        codes[name] = code

    return codes


def make_pythran_code_functions(functions, signatures_func, codes_functions):

    code_pythran = ""

    for name_func in functions:

        try:
            signatures = signatures_func[name_func]
        except KeyError:
            logger.warning("No Pythran signature for function " + name_func)
            continue

        for signature in signatures:
            code_pythran += f"# pythran export {signature}\n"

        code = codes_functions[name_func]

        code_pythran += f"\n{code}\n\n"

    return code_pythran


def make_pythran_code(path_py):
    """Create a pythran code from a Python file"""

    with open(path_py) as file:
        code = file.read()

    namespace = None
    if "# FLUIDPYTHRAN_NO_IMPORT" not in code:
        # we have to import the module!
        fluidpythran.is_compiling = True
        try:
            namespace = run_path(str(path_py))
        except ImportError:
            name_mod = ".".join(
                path_py.absolute().relative_to(os.getcwd()).with_suffix("").parts
            )
            namespace = run_module(name_mod)
        fluidpythran.is_compiling = False

    (
        blocks,
        signatures_blocks,
        code_blocks,
        functions,
        signatures_func,
        imports,
    ) = parse_py_code(code)

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

    code_pythran = ""
    if imports:
        code_pythran += "\n" + "\n".join(imports) + "\n"

    module_name = Path(path_py).with_suffix("").name
    if module_name in fluidpythran._modules:
        fp = fluidpythran._modules[module_name]
        fp._make_signatures_from_annotations()
        functions = fp.functions.keys()
        signatures_func_annot = fp.signatures_func
        codes_functions = get_codes_from_functions(fp.functions)

        # merge signatures introduced by type annotations and by Pythran commands
        signatures_func_all = signatures_func.copy()
        for name_func, signatures in signatures_func_annot.items():
            if name_func not in signatures_func_all:
                signatures_func_all[name_func] = []
            signatures_func_all[name_func].extend(signatures)
    else:
        codes_functions = get_code_functions(code, functions)
        signatures_func_all = signatures_func

    code_pythran += make_pythran_code_functions(
        functions, signatures_func_all, codes_functions
    )

    # blocks...

    # we check that some types correspond to fluidpythran types
    # we can do that only if the module has been imported

    types_variables_blocks = {}
    return_block = {}
    for name_block, list_str_types_variables in signatures_blocks.items():
        types_variables_blocks[name_block] = []

        for str_types_variables in list_str_types_variables:
            types_variables = {}
            lines = str_types_variables.split("(", 1)[1].split(")")[0].split(";")
            for line in lines:
                type_, str_variables = line.strip().split(" ", 1)

                if namespace is not None and type_ in namespace:
                    type_ = namespace[type_]
                else:
                    try:
                        type_ = eval(type_)
                    except SyntaxError:
                        pass

                variables = [
                    variable.replace(",", "").strip()
                    for variable in str_variables.split(",")
                ]

                types_variables[type_] = variables

            types_variables_blocks[name_block].append(types_variables)

            if list_str_types_variables and "->" in str_types_variables:
                return_block[name_block] = str_types_variables.split("->", 1)[1]

    for name_block, list_types_variables in tuple(types_variables_blocks.items()):
        new_list_types_variables = []
        for types_variables in list_types_variables:
            sequence_types = compute_pythran_types_from_valued_types(
                types_variables.keys()
            )
            variabless = types_variables.values()
            # print("variabless", variabless)
            for types in sequence_types:
                new_types_variables = {}
                for type_, variables in zip(types, variabless):
                    if type_ not in new_types_variables:
                        new_types_variables[type_] = variables
                    else:
                        new_types_variables[type_] = new_types_variables[type_] + variables
                new_list_types_variables.append(new_types_variables)

        types_variables_blocks[name_block] = new_list_types_variables

    # print("types_variables_blocks", types_variables_blocks)

    variables_types_block = {}
    for name_block, list_types_variables in types_variables_blocks.items():
        variables_types_block[name_block] = []
        for types_variables in list_types_variables:
            variables_types = {}
            for type_, variables in types_variables.items():
                for variable in variables:
                    variables_types[variable] = type_
                variables_types

            variables_types_block[name_block].append(variables_types)

    # print("variables_types_block", variables_types_block)

    arguments_blocks = {}

    for name_block, list_variables_types in variables_types_block.items():
        # add "pythran export" for blocks

        # print("list_variables_types", list_variables_types)

        tmp = []

        for variables_types in list_variables_types:
            if variables_types in tmp:
                continue
            tmp.append(variables_types)
            str_types = variables_types.values()
            str_variables = ", ".join(str_types)
            code_pythran += f"# pythran export {name_block}({str_variables})\n"

        # add code for blocks
        variables = list_variables_types[0].keys()
        arguments_blocks[name_block] = list(variables)

        str_variables = ", ".join(variables)

        code_pythran += f"\ndef {name_block}({str_variables}):\n"

        code_block = code_blocks[name_block]

        code_pythran += 4 * " " + code_block.replace("\n", "\n" + 4 * " ") + "\n"

        if name_block in return_block:
            code_pythran += f"    return {return_block[name_block]}\n"

    if arguments_blocks:
        code_pythran += "# pythran export arguments_blocks\n"
        code_pythran += "arguments_blocks = " + str(arguments_blocks) + "\n"

    if code_pythran:
        code_pythran += (
            "\n# pythran export __fluidpythran__\n"
            f"__fluidpythran__ = ('{fluidpythran.__version__}',)"
        )

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
