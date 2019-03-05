from pathlib import Path

# import ast
import gast as ast
import beniget
import astunparse
from pprint import pprint

from capturex import CaptureX, make_code_external


def dump(node):
    print(astunparse.dump(node))


path_examples = Path("examples")

files = sorted(path_examples.glob("*.py"))

with open(files[3]) as file:
    code = file.read()

module = ast.parse(code)

duc = beniget.DefUseChains()
duc.visit(module)

ancestors = beniget.Ancestors()
ancestors.visit(module)

udc = beniget.UseDefChains(duc)


functions_boosted = {}
class_boosted = {}
methods_boosted = {}

# we first need to find the node where transonic.boost is defined...


def add_definition(definition_node):
    tmp_boosted = None
    key = definition_node.name
    if isinstance(definition_node, ast.FunctionDef):
        parent = ancestors.parent(definition_node)
        if isinstance(parent, ast.ClassDef):
            tmp_boosted = methods_boosted
            key = (parent.name, key)
        else:
            tmp_boosted = functions_boosted
    elif isinstance(definition_node, ast.ClassDef):
        tmp_boosted = class_boosted
    if tmp_boosted is not None:
        tmp_boosted[key] = definition_node


for node in module.body:
    if isinstance(node, ast.Import):
        for alias in node.names:
            if alias.name == "transonic":
                transonic_def_node = alias
                transonic_def = duc.chains[transonic_def_node]
                for user in transonic_def.users():
                    for user1 in user.users():
                        if (
                            isinstance(user1.node, ast.Attribute)
                            and user1.node.attr == "boost"
                        ):
                            definition_node = ancestors.parent(user1.node)
                            add_definition(definition_node)
    elif isinstance(node, ast.ImportFrom):
        if node.module == "transonic":
            for alias in node.names:
                if alias.name == "boost":
                    boost_def_node = alias
                    boost_def = duc.chains[boost_def_node]
                    for user in boost_def.users():
                        definition_node = ancestors.parent(user.node)
                        add_definition(definition_node)


pprint(functions_boosted)
pprint(methods_boosted)
pprint(class_boosted)

objects = []

for boosted in (functions_boosted, methods_boosted):
    for fdef in boosted.values():
        fdef.decorator_list = []
        objects.append(fdef)

for cdef in class_boosted.values():
    objects.append(cdef)

capturex_annotations = CaptureX(
    objects,
    module,
    defuse_chains=duc,
    usedef_chains=udc,
    ancestors=ancestors,
    consider_annotations="only",
)

code_dependance_annotations = make_code_external(capturex_annotations.external)

capturex = CaptureX(
    objects,
    module,
    defuse_chains=duc,
    usedef_chains=udc,
    ancestors=ancestors,
    consider_annotations=False,
)

code_dependance = make_code_external(capturex.external)
