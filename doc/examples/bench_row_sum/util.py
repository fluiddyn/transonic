import numpy as np

from transonic.util import timeit
from transonic.config import backend_default


def check(functions, arr, columns):
    res0 = functions[0](arr, columns)
    for func in functions[1:]:
        assert np.allclose(res0, func(arr, columns))
    print("Checks passed: results are consistent")


def bench(functions, arr, columns):
    print(backend_default.capitalize())
    for func in functions:
        result = timeit("func(arr, columns)", globals=locals())
        print(f"{func.__name__:20s} {result:.3e} s")
    print()
