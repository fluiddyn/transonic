# __protected__ from numba import njit
# __protected__ @njit(cache=True, fastmath=True)


def compute(a, b, c, d, e):
    print(e)
    tmp = a + b
    if 1 and 2:
        tmp *= 2
    return tmp


__transonic__ = ("0.4.7",)
