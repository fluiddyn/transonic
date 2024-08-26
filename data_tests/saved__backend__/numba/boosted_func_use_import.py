# __protected__ from numba import njit
import numpy as np
from __ext__func__exterior_import_boost import func_import

# __protected__ @njit(cache=True, fastmath=True)


def func(a, b):
    return (a * np.log(b)).max() + func_import()


# __protected__ @njit(cache=True, fastmath=True)


def __transonic__():
    return "0.7.1"
