# __protected__ from numba import njit
# __protected__ @njit(cache=True, fastmath=True)


def gen_seq(dtype, seq_type, n):
    return seq_type(map(dtype, range(n)))


def __transonic__():
    return "0.7.3"
