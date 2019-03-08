from pathlib import Path
from pprint import pprint

from transonic.analyses import analyse_aot
from transonic.analyses.util import print_dumped

path_examples = Path("examples")

paths = sorted(path_examples.glob("*.py"))
path = paths[4]

# path = Path("~/Dev/fluidsim/fluidsim/base/time_stepping/pseudo_spect.py")

with open(path.expanduser()) as file:
    code = file.read()

boosted_dicts, code_dependance, annotations, blocks, blocks_parsed = analyse_aot(
    code
)

pprint(boosted_dicts)
print(code_dependance)
pprint(annotations)
# pprint(blocks)

# for block in blocks:
#     print(f"signatures block {block.name}:")
#     pprint(block.signatures)
