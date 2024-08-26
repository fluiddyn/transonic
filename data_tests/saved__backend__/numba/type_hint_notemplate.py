# __protected__ from numba import njit
# __protected__ @njit(cache=True, fastmath=True)


def compute(a, b, c, d, e):
    print(e)
    tmp = a + b
    if 1 and 2:
        tmp *= 2
    return tmp


def __transonic__():
    return "0.7.1"
