# __protected__ from numba import njit
# __protected__ @njit


def func(a=1, b=None, c=1.0):
    print(b)
    return a + c


__transonic__ = ("0.4.0",)
