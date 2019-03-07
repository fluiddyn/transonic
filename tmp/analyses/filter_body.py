from pathlib import Path

import gast as ast
import beniget


from transonic.analyses.util import (
    get_annotations,
    print_ast,
    print_dump,
    print_unparsed,
    filter_code_typevars
)


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


code_filtered = filter_code_typevars(module, duc, ancestors)

print(code_filtered)