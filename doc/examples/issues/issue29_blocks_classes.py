"""
See https://bitbucket.org/fluiddyn/fluidpythran/issues/29/

"""
from fluidpythran import boost, with_blocks, block


def non_pythranizable(arg):
    """represent a function that can not be compiled by Pythran"""
    return arg


@boost
class MyClass:

    attr0: int

    @with_blocks
    def func(self, arg: int):

        a = non_pythranizable(arg)

        with block(a=float):
            tmp = a + arg + self.attr0

        return non_pythranizable(tmp)
