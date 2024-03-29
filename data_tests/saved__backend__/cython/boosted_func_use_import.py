try:
    import cython
except ImportError:
    from transonic_cl import cython

import numpy as np
from __ext__func__exterior_import_boost import func_import


def func(a, b):
    return (a * np.log(b)).max() + func_import()


__transonic__ = ("0.3.3",)
