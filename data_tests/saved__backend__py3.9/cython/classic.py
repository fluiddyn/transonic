try:
    import cython
except ImportError:
    from transonic_cl import cython

import numpy as np


def func(a, b):
    return (a * np.log(b)).max()


__transonic__ = ("0.3.3",)
