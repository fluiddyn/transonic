from pathlib import Path

# import ast
import gast as ast
import beniget
import astunparse
from pprint import pprint

from capturex import CaptureX, make_code_external

from transonic.analyses.util import get_annotations, print_ast, print_dump, filter_code_typevars


path_examples = Path("examples")

files = sorted(path_examples.glob("*.py"))

with open(files[1]) as file:
    code = file.read()

print("ast.parse")
module = ast.parse(code)

print("compute DefUseChains")
duc = beniget.DefUseChains()
duc.visit(module)

print("compute Ancestors")
ancestors = beniget.Ancestors()
ancestors.visit(module)

print("compute UseDefChains")
udc = beniget.UseDefChains(duc)


functions_boosted = {}
classes_boosted = {}
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
        tmp_boosted = classes_boosted
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


print("functions:")
pprint(functions_boosted)
print("methods:")
pprint(methods_boosted)
print("classes:")
pprint(classes_boosted)

boosteds = {"functions": functions_boosted, "methods": methods_boosted, "classes": classes_boosted}

objects = []

for boosted in boosteds.values():
    for definition in boosted.values():
        objects.append(definition)


code_dependance_annotations = filter_code_typevars(module, duc, ancestors)

capturex = CaptureX(
    objects,
    module,
    defuse_chains=duc,
    usedef_chains=udc,
    ancestors=ancestors,
    consider_annotations=False,
)

code_dependance = make_code_external(capturex.external)

namespace = {}
exec(code_dependance_annotations, namespace)


annotations = {}

for kind, boosted in boosteds.items():
    annotations[kind] = {}

    for key, definition in boosted.items():
        annotations[kind][key] = get_annotations(definition, namespace)

pprint(annotations)
