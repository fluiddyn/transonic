import beniget
import gast as ast
import astunparse

from capturex import CaptureX

examples = {6: "issue6_import.py", 7: "issue7_func.py"}


with open(examples[6]) as file:
    code = file.read()

module = ast.parse(code)

duc = beniget.DefUseChains()
duc.visit(module)

ancestors = beniget.Ancestors()
ancestors.visit(module)

boost = [d for d in duc.locals[module] if d.name() == "boost"][0]

for user in boost.users():
    # we're interested in the parent of the decorator
    parents = ancestors.parents[user.node]
    # direct parent of the decorator is the function
    fdef = parents[-1]
    print(fdef.name)

chain = duc.chains[fdef]

for node in fdef.decorator_list:
    if node.id == "boost":
        fdef.decorator_list.remove(node)


capturex = CaptureX(module, fdef)

capturex.visit(fdef)

for node in capturex.external:
    print(astunparse.dump(node))
    print(astunparse.unparse(node))
