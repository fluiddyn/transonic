# __protected__ from numba import njit
# __protected__ @njit(cache=True, fastmath=True)


def func(x):
    return x**2


# __protected__ @njit(cache=True, fastmath=True)


def __transonic__():
    return "0.7.1"
