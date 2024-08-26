try:
    import cython
except ImportError:
    from transonic_cl import cython

import numpy as np


def func(a, b):
    return (a * np.log(b)).max()


def __transonic__():
    return "0.7.1"
