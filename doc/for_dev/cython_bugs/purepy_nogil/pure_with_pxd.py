# cython: language_level=3
import cython


def add(a, b):
    return a + b


def use_add(n):
    result = 1
    with cython.nogil:
        for i in range(n):
            result = add(result, result)
    return result
