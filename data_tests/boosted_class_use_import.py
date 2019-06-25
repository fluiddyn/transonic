import numpy as np

from transonic import boost
from exterior_import_boost import func_import


@boost
class MyClass2:
    attr0: int
    attr1: int

    def __init__(self):
        self.attr0 = self.attr1 = 1

    @boost
    def myfunc(self, arg: int):
        return self.attr1 + self.attr0 + np.abs(arg) + func_import()

    def check(self):
        assert self.myfunc(1) == 5
