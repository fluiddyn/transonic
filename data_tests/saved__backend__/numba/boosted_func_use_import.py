# __protected__ from numba import njit
import numpy as np
from exterior_import_boost import func_import

# __protected__ @njit(cache=True, fastmath=True)


def func(a, b):
    return (a * np.log(b)).max() + func_import()


__transonic__ = ("0.4.7",)
