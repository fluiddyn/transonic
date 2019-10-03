
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
    file.write(code.format(package="future"))

print(getoutput("TRANSONIC_BACKEND='cython' python tmp.py"))
# print(getoutput("TRANSONIC_BACKEND='pythran' python tmp.py"))
# print(getoutput("TRANSONIC_BACKEND='numba' python tmp.py"))
# print(getoutput("TRANSONIC_NO_REPLACE=1 python tmp.py"))

with open("tmp.py", "w") as file:
    file.write(code.format(package="pyx"))

print(getoutput("python tmp.py"))