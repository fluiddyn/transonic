# __protected__ from numba import njit
# __protected__ @njit


def func():
    return 1


# __protected__ @njit


def func2():
    return 1


__transonic__ = ("0.3.0.post0",)
