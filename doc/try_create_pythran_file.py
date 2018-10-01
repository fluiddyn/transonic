from tokenize import (
    tokenize,
    untokenize,
    COMMENT,
    INDENT,
    DEDENT,
    OP,
    STRING,
    NAME,
)
from token import tok_name
from io import BytesIO

path = "example_class.py"

blocks = []

with open(path) as file:
    code = file.read()

has_to_find_name_block = False

g = tokenize(BytesIO(code.encode("utf-8")).readline)
for toknum, tokval, a, b, c in g:

    if toknum == NAME and tokval == "use_pythranized_block":
        has_to_find_name_block = True

    if has_to_find_name_block and toknum == STRING:
        name_block = eval(tokval)
        print("Block", name_block)
        has_to_find_name_block = False
        blocks.append(name_block)

    print((tok_name[toknum], tokval))

print(blocks)
