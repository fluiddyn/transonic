# __protected__ from numba import njit
# __protected__ @njit(cache=True, fastmath=True)


def func():
    return 1


# __protected__ @njit(cache=True, fastmath=True)


def func2():
    return 1


# __protected__ @njit(cache=True, fastmath=True)


def __transonic__():
    return "0.7.1"
