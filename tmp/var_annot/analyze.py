
import gast as ast

from transonic.analyses.capturex import CaptureX
from transonic.analyses import extast
from transonic.analyses import analyse_aot
from transonic.analyses.util import print_dumped, print_unparsed

from transonic.backends import backends

backend = backends["cython"]

path_file = "simple.py"

with open(path_file) as file:
    code = file.read()

boosted_dicts, code_dependance, annotations, blocks, code_ext = analyse_aot(code, path_file)

module = extast.parse(code)

for node in module.body:
    if isinstance(node, ast.FunctionDef):
        fdef = node
        break

# annotations_locals = annotations["__locals__"]

# annot = annotations["functions"][fdef.name]

# fdef.body = []
# fdef.decorator_list = []

# print_unparsed(fdef)

print("\n".join(backend.get_signatures(fdef.name, fdef, annotations)))

# print_dumped("""
# @cython.locals(result=np.float64_t, i=cython.int)
# def mysum(arr_input):
#     pass
# """)
