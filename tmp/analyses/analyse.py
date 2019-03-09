from pathlib import Path

from transonic.analyses.util import print_dumped


from transonic.backends.pythran import make_pythran_code

path_examples = Path("examples")

paths = sorted(path_examples.glob("*.py"))
path = paths[4]

# path = Path("~/Dev/fluidsim/fluidsim/base/time_stepping/pseudo_spect.py")

code = make_pythran_code(path)

print(code)
