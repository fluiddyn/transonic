# __protected__ from numba import njit
# __protected__ @njit(cache=True, fastmath=True)


def block0(a, b, n):
    # transonic block (
    #     A a; A1 b;
    #     int n
    # )
    # transonic block (
    #     int[:] a, b;
    #     float n
    # )
    result = ((a ** 2) + (b.mean() ** 3)) + n
    return result


arguments_blocks = {"block0": ["a", "b", "n"]}
__transonic__ = ("0.4.7",)
