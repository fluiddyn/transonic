# __protected__ from numba import njit
import numpy as np

# __protected__ @njit


def block0(a, b, n):
    # foo
    # transonic block (
    #     float[][] a, b;
    #     int n
    # ) bar
    # foo
    # transonic block (
    #     float[][][] a, b;
    #     int n
    # )
    # foobar
    result = np.zeros_like(a)
    for _ in range(n):
        result += (a ** 2) + (b ** 3)
    return result


# __protected__ @njit


def block1(a, b, n):
    # transonic block (
    #     float[][] a, b;
    #     int n
    # )
    # transonic block (
    #     float[][][] a, b;
    #     int n
    # )
    result = np.zeros_like(a)
    for _ in range(n):
        result += (a ** 2) + (b ** 3)
    return result


arguments_blocks = {"block0": ["a", "b", "n"], "block1": ["a", "b", "n"]}
__transonic__ = ("0.3.0.post0",)
