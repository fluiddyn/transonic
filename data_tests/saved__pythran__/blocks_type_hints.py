# pythran export block0(complex[:, :], complex[:, :, :], int)
# pythran export block0(complex[:], complex[:, :], int)
# pythran export block0(float[:, :], float[:, :, :], int)
# pythran export block0(float[:], float[:, :], int)
# pythran export block0(int[:], int[:], float)


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


# pythran export arguments_blocks
arguments_blocks = {"block0": ["a", "b", "n"]}

# pythran export __transonic__
__transonic__ = ("0.2.1",)
