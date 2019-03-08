from tokenize import tokenize, untokenize, COMMENT, INDENT, DEDENT, STRING, NAME
from io import BytesIO

from ..log import logger


def parse_code(code: str):
    """Parse the code of a .py file and return data"""

    blocks = []
    signatures_blocks = {}
    code_blocks = {}

    functions = set()
    signatures_func = {}

    has_to_find_name_block = False
    has_to_find_signatures = False
    has_to_find_code_block = False
    in_def = False

    g = tokenize(BytesIO(code.encode("utf-8")).readline)
    for toknum, tokval, a, b, c in g:

        if toknum == NAME and tokval == "use_block":
            has_to_find_name_block = True
            has_to_find_signatures = True
            has_to_find_code_block = "after use_block"

        if has_to_find_name_block and toknum == STRING:
            name_block = eval(tokval)
            has_to_find_name_block = False
            blocks.append(name_block)

        if toknum == COMMENT and tokval.startswith("# transonic def "):
            in_def = True
            signature_func = tokval.split("# transonic def ", 1)[1]
            name_func = signature_func.split("(")[0]
            functions.add(name_func)

            if name_func not in signatures_func:
                signatures_func[name_func] = []

            if ")" in tokval:
                in_def = False
                signatures_func[name_func].append(signature_func)

        if in_def:
            if toknum == COMMENT:
                if "# transonic def " in tokval:
                    tokval = tokval.split("(", 1)[1]
                signature_func += tokval.replace("#", "").strip()
                if ")" in tokval:
                    in_def = False
                    signatures_func[name_func].append(signature_func)

        if has_to_find_signatures and toknum == COMMENT:
            if tokval.startswith("# transonic block "):
                in_signature = True
                signature = tokval.split("# transonic block ", 1)[1]
            elif in_signature:
                signature += tokval[1:].strip()
                if ")" in tokval or tokval.endswith(")"):
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

        if has_to_find_code_block == "after use_block" and toknum == INDENT:
            has_to_find_code_block = "in block"
            code_blocks[name_block] = []

        # logger.debug((tok_name[toknum], tokval))

    return blocks, signatures_blocks, code_blocks, signatures_func
