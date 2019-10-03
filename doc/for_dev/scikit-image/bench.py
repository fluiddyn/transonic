from subprocess import getoutput

setup = """
import numpy as np
from {package}.cmorph import _dilate

rows = 1024
cols = 1024
srows = 64
scols = 64

image = np.random.randint(0, 255, rows * cols, dtype=np.uint8).reshape(
    (rows, cols)
)
selem = np.random.randint(0, 1, srows * scols, dtype=np.uint8).reshape(
    (srows, scols)
)
out = np.zeros((rows, cols), dtype=np.uint8)
shift_x = np.int8(2)
shift_y = np.int8(2)

"""

stmt = "_dilate(image, selem, out, shift_x, shift_y)"


code = f"""
from transonic.util import timeit

setup = '''{setup}'''
stmt = '''{stmt}'''

print(timeit(stmt, setup, total_duration=2))

"""

with open("tmp.py", "w") as file:
    file.write(code.format(package="pyx"))

time_old = float(getoutput("python tmp.py"))

print(f'cython "skimage" {time_old:.2e} s  (= norm)')

with open("tmp.py", "w") as file:
    file.write(code.format(package="future"))

for backend in ("cython", "pythran", "numba"):
    time = float(getoutput(f"TRANSONIC_BACKEND='{backend}' python tmp.py"))
    print(f"{backend:16s} {time:.2e} s  (= {time/time_old:.4f} * norm)")

# print(getoutput("TRANSONIC_NO_REPLACE=1 python tmp.py"))
