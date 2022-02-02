# __protected__ from numba import njit
# __protected__ @njit(cache=True, fastmath=True)


def func(x):
    return x**2


__transonic__ = ("0.4.7",)
