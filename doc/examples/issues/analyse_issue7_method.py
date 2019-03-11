import beniget
import gast as ast
import astunparse

from capturex import CaptureX


def dump(node):
    print(astunparse.dump(node))


with open("issue7_method.py") as file:
    code = file.read()

module = ast.parse(code)

duc = beniget.DefUseChains()
duc.visit(module)

ucc = beniget.UseDefChains(duc)

ancestors = beniget.Ancestors()
ancestors.visit(module)

boost = [d for d in duc.locals[module] if d.name() == "boost"][0]

chain = duc.chains[boost.node]
users = chain.users()

class_defs = []
function_defs = []

for user in users:
    func_or_class_def = ancestors.parent(user.node)
    if isinstance(func_or_class_def, ast.ClassDef):
        class_defs.append(func_or_class_def)
    elif isinstance(func_or_class_def, ast.FunctionDef):
        function_defs.append(func_or_class_def)


for fdef in function_defs:
    for node in fdef.decorator_list:
        if node.id == "boost":
            fdef.decorator_list.remove(node)

    capturex = CaptureX(module, fdef)

    capturex.visit(fdef)

    for node in capturex.external:
        # print(astunparse.dump(node))
        print(astunparse.unparse(node).strip())
