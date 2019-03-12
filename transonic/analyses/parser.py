from tokenize import tokenize, COMMENT
from io import BytesIO


def parse_code(code: str):
    """Parse the code of a .py file and return data"""

    functions = set()
    signatures_func = {}

    in_def = False

    g = tokenize(BytesIO(code.encode("utf-8")).readline)
    for toknum, tokval, a, b, c in g:
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

    return signatures_func
