import numpy as np

# pythran export block0(float[][], float[][], int)
# pythran export block0(float[][][], float[][][], int)


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


# pythran export block1(float[][], float[][], int)
# pythran export block1(float[][][], float[][][], int)


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


# pythran export arguments_blocks
arguments_blocks = {"block0": ["a", "b", "n"], "block1": ["a", "b", "n"]}

# pythran export __transonic__
__transonic__ = ("0.2.1",)
