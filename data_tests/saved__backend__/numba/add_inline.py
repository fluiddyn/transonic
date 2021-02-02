# __protected__ from numba import njit
# __protected__ @njit(cache=True, fastmath=True)


def add(a, b):
    return a + b


# __protected__ @njit(cache=True, fastmath=True)


def use_add(n=10000):
    tmp = 0
    for _ in range(n):
        tmp = add(tmp, 1)
    return tmp


__transonic__ = ("0.4.7",)
