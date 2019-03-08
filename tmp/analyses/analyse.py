from pathlib import Path
from pprint import pprint

from transonic.analyses import analyse_aot


path_examples = Path("examples")

paths = sorted(path_examples.glob("*.py"))
path = paths[5]

path = Path("~/Dev/fluidsim/fluidsim/base/time_stepping/pseudo_spect.py")

with open(path.expanduser()) as file:
    code = file.read()

boosted_dicts, code_dependance, annotations, blocks = analyse_aot(code)

pprint(boosted_dicts)
pprint(code_dependance)
pprint(annotations)
# pprint(blocks)

for block in blocks:
    print(f"signatures block {block.name}:")
    pprint(block.signatures)