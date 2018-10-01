
from tokenize import tokenize, untokenize
from io import BytesIO

path = "example_class.py"

with open(path) as file:
    code = file.read()


g = tokenize(BytesIO(code.encode('utf-8')).readline)
for toknum, tokval, a, b, c in g:
    print((toknum, tokval, a, b, c))
