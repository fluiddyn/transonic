"""
See https://foss.heptapod.net/fluiddyn/transonic/issues/6

"""
from transonic import with_blocks, block

T = int


def non_pythranizable(arg):
    """represent a function that can not be compiled by Pythran"""
    return arg


@with_blocks
def func0(arg: int):

    a = b = non_pythranizable(arg)
    c: float = 1.2

    with block():
        # transonic signature(
        #     T a, b
        # )

        # transonic signature(
        a: int
        b: float
        # )

        return a + b + c + arg


@with_blocks
def func1(arg: int):

    a = non_pythranizable(arg)

    with block():
        a: int
        tmp = a + arg

    return non_pythranizable(tmp)
