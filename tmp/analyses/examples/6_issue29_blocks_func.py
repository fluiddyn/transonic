"""
See https://bitbucket.org/fluiddyn/fluidpythran/issues/29/

"""
from transonic import with_blocks, block


def non_pythranizable(arg):
    """represent a function that can not be compiled by Pythran"""
    return arg


@with_blocks
def func0(arg: int):

    a = non_pythranizable(arg)

    with block(a=float):
        return a + arg


@with_blocks
def func1(arg: int):

    a = non_pythranizable(arg)

    with block(a=float):
        tmp = a + arg

    return non_pythranizable(tmp)
