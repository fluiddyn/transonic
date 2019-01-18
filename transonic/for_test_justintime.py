import numpy as np

# transonic import numpy as np

from transonic import jit, include, boost
from .mpi import Path


@include(used_by="func1")
def func0(a):
    return 2 * a


@include(used_by="func1")
def func():
    return 1


@jit
def func1(a: "int[][] or float[]", l: "int list"):
    tmp = np.exp(sum(l))
    result = tmp * a * func0(a) + func()
    return result


@jit()
def func2(a):
    return a


# weird but done on purpose for a better coverage
Path(__file__).touch()


@jit()
def func2(a):
    return a


@jit()
def func_dict(d: "str: float dict"):
    return d.popitem()


@boost
class MyClass:
    def __init__(self):
        self.attr0 = self.attr1 = 1

    @jit
    def myfunc(self, arg):
        return self.attr1 + self.attr0 + arg

    def check(self):
        assert self.myfunc(1) == 3
