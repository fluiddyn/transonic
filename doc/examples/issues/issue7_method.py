"""
See https://bitbucket.org/fluiddyn/fluidpythran/issues/7/

The function `add` is used in the "boosted" method `compute` and we don't use
`fluidpythran.include`.

"""
from fluidpythran import boost


def add(a, b):
    return a + b


@boost
class MyClass:
    attr0: float
    attr1: float

    def __init__(self, arg):
        self.attr0 = self.attr1 = 2 * float(arg)

    @boost
    def compute(self, number: int):
        result = 0.0
        for _ in range(number):
            result += add(self.attr0, self.attr1)
