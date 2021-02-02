# __protected__ from numba import njit
import numpy as np

# __protected__ @njit(cache=True, fastmath=True)


def func(a, b):
    return (a * np.log(b)).max()


# __protected__ @njit(cache=True, fastmath=True)


def func1(a, b):
    return a * np.cos(b)


__transonic__ = ("0.4.7",)
