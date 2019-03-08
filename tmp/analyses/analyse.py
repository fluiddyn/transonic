from pathlib import Path

import gast as ast
import astunparse
from pprint import pprint

from transonic.analyses.capturex import CaptureX, make_code_external

from transonic.analyses import compute_ancestors_chains, get_boosted_dicts

from transonic.analyses.util import (
    print_dumped,
    print_unparsed,
    get_annotations,
    filter_code_typevars,
)
from transonic.analyses.blocks_if import get_block_definitions


path_examples = Path("examples")

files = sorted(path_examples.glob("*.py"))

with open(files[4]) as file:
    code = file.read()

print("ast.parse")
module = ast.parse(code)

print("compute ancestors and chains")
ancestors, duc, udc = compute_ancestors_chains(module)

print("filter_code_typevars")
code_dependance_annotations = filter_code_typevars(module, duc, ancestors)
print(code_dependance_annotations)


print("find boosted objects")
boosted_dicts = get_boosted_dicts(module, ancestors, duc)
pprint(boosted_dicts)

print("compute code dependance")

def_nodes = [
    def_node
    for boosted_dict in boosted_dicts.values()
    for def_node in boosted_dict.values()
]

# remove the decorator (boost) to compute the code dependance
for def_node in def_nodes:
    def_node.decorator_list = []

capturex = CaptureX(
    def_nodes,
    module,
    ancestors=ancestors,
    defuse_chains=duc,
    usedef_chains=udc,
    consider_annotations=False,
)

code_dependance = make_code_external(capturex.external)
print(code_dependance)


print("compute the annotations")
namespace = {}
exec(code_dependance_annotations, namespace)

annotations = {}

for kind, boosted_dict in boosted_dicts.items():
    annotations[kind] = {}

    for key, definition in boosted_dict.items():
        annotations[kind][key] = get_annotations(definition, namespace)

pprint(annotations)

print("get_block_definitions")
blocks = get_block_definitions(code, module, ancestors, duc, udc)
pprint(blocks)