from subprocess import getoutput
from pathlib import Path

statements = {
    ("cmorph", "_dilate"): "_dilate(image, selem, out, shift_x, shift_y)",
    (
        "_greyreconstruct",
        "reconstruction_loop",
    ): "reconstruction_loop(ranks, prev, next_, strides, current_idx, image_stride)",
}

name_module = "cmorph"
name_function = "_dilate"

name_module = "_greyreconstruct"
name_function = "reconstruction_loop"

print(f"module: {name_module}")
stmt = statements[(name_module, name_function)]
print(stmt)

path_setup = Path("setup_codes") / f"{name_module}_{name_function}.py"

if not path_setup.exists():
    raise RuntimeError

with open(path_setup) as file:
    setup = file.read()

setup_pyx = setup.replace(
    f"from future.{name_module} import", f"from pyx.{name_module} import"
)

code_pyx = f"""
from transonic.util import timeit
setup = '''{setup_pyx}'''
stmt = '''{stmt}'''
print(timeit(stmt, setup, total_duration=2))
"""

code = f"""
from transonic.util import timeit
setup = '''{setup}'''
stmt = '''{stmt}'''
print(timeit(stmt, setup, total_duration=2))
"""

with open("tmp.py", "w") as file:
    file.write(code_pyx)

time_old = float(getoutput("python tmp.py"))

print(f'cython "skimage" {time_old:.2e} s  (= norm)')

with open("tmp.py", "w") as file:
    file.write(code.format(package="future"))

for backend in ("cython", "pythran", "numba"):
    time = float(getoutput(f"TRANSONIC_BACKEND='{backend}' python tmp.py"))
    print(f"{backend:16s} {time:.2e} s  (= {time/time_old:.4f} * norm)")

# print(getoutput("TRANSONIC_NO_REPLACE=1 python tmp.py"))
