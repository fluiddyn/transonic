
import gast as ast

from transonic.analyses.capturex import CaptureX
from transonic.analyses import extast
from transonic.analyses.util import print_dumped, print_unparsed, extract_variable_annotations

with open("simple.py") as file:
    code = file.read()


module = extast.parse(code)

# print_dumped(module)

for node in module.body:
    if isinstance(node, ast.FunctionDef):
        fdef = node
        break

capturex = CaptureX([fdef], module, consider_annotations="only")

code_dependance_annotations = capturex.make_code_external()

namespace = {}
exec(code_dependance_annotations, namespace)

print(extract_variable_annotations(fdef, namespace))