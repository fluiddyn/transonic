import beniget
import gast as ast


with open("issue6_import.py") as file:
    code = file.read()

module = ast.parse(code)

duc = beniget.DefUseChains()
duc.visit(module)

ancestors = beniget.Ancestors()
ancestors.visit(module)

boost = [d for d in duc.locals[module] if d.name() == "boost"][0]

for use in boost.uses:
    # we're interested in the parent of the decorator
    parents = ancestors.parents[use.node]
    # direct parent of the decorator is the function
    fdef = parents[-1]
    print(fdef.name)

chain = duc.chains[fdef]


class Capture(ast.NodeVisitor):
    def __init__(self, module_node):
        # initialize def-use chains
        self.duc = beniget.DefUseChains()
        self.duc.visit(module_node)
        self.uses_local_def = set()  # uses of local definitions
        self.captured = set()  # identifiers that don't belong to local uses

    def visit_FunctionDef(self, node):
        # initialize the set of node using a local variable
        for def_ in self.duc.locals[node]:
            print("def_.name()", def_.name())
            print(list((use.name(), use.node.ctx) for use in def_.uses))
            self.uses_local_def.update(use.node for use in def_.uses)

        self.generic_visit(node)

    def visit_Name(self, node):
        # register load of identifiers not locally defined
        print("node.id", node.id, node.ctx)
        if isinstance(node.ctx, ast.Load):
            if node not in self.uses_local_def:
                self.captured.add(node)


capture = Capture(module)

for node in fdef.decorator_list:
    if node.id == "boost":
        fdef.decorator_list.remove(node)

capture.visit(fdef)

print(list(node.id for node in capture.captured))

node = next(iter(capture.captured))
