import numpy as np
from transonic import jit


@jit(backend="numba")
def fib(n):
    if n < 2:
        return n
    return np.add(fib(n - 1), fib(n - 2))


@jit
def fib2(n):
    if n < 2:
        return n
    return np.add(fib2(n - 1), fib2(n - 2))
