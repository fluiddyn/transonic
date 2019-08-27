from timeit import timeit

import numpy as np

from transonic.config import backend_default


def check(functions, arr, columns):
    res0 = functions[0](arr, columns)
    for func in functions[1:]:
        assert np.allclose(res0, func(arr, columns))
    print("Checks passed: results are consistent")


def bench(functions, arr, columns):
    print(backend_default.capitalize())
    number = 1000
    coef = 1
    if backend_default == "python":
        coef = 10
    number //= coef
    for func in functions:
        result = timeit(lambda: func(arr, columns), number=number)
        print(f"{func.__name__:20s} {coef * result:.2f} s")
