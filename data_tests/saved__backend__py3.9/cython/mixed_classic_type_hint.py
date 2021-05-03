try:
    import cython
except ImportError:
    from transonic_cl import cython

import numpy as np


def func(a, b):
    return (a * np.log(b)).max()


def func1(a, b):
    return a * np.cos(b)


__transonic__ = ("0.3.3",)
