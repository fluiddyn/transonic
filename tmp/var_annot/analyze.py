
import gast as ast

from transonic.analyses.capturex import CaptureX
from transonic.analyses import extast
from transonic.analyses.util import print_dumped, print_unparsed

with open("simple.py") as file:
    code = file.read()


module = extast.parse(code)

# print_dumped(module)

for node in module.body:
    if isinstance(node, ast.FunctionDef):
        fdef = node
        break

capturex = CaptureX([fdef], module, consider_annotations="only")

code_ext = capturex.make_code_external()

print("code:", code_ext, sep="\n")