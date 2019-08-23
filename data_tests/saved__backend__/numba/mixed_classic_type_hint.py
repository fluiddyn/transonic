# __protected__ from numba import njit
import numpy as np

# __protected__ @njit


def func(a, b):
    return (a * np.log(b)).max()


# __protected__ @njit


def func1(a, b):
    return a * np.cos(b)


__transonic__ = ("0.3.0.post0",)
