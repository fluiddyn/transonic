import numpy as np
from mod1 import func_import

from transonic import boost, jit


@boost
class MyClass2:
    def __init__(self):
        self.attr0 = self.attr1 = 1

    @jit()
    def myfunc(self, arg):
        return self.attr1 + self.attr0 + np.abs(arg) + func_import()

    def check(self):
        assert self.myfunc(1) == 4
