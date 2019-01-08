import numpy as np

# pythran import numpy as np

from transonic import cachedjit, include, boost
from .mpi import Path


@include(used_by="func1")
def func0(a):
    return 2 * a


@include(used_by="func1")
def func():
    return 1


@cachedjit
def func1(a: "int[][] or float[]", l: "int list"):
    tmp = np.exp(sum(l))
    result = tmp * a * func0(a) + func()
    return result


@cachedjit()
def func2(a):
    return a


# weird but done on purpose for a better coverage
Path(__file__).touch()


@cachedjit()
def func2(a):
    return a


@cachedjit()
def func_dict(d: "str: float dict"):
    return d.popitem()


@boost
class MyClass:
    def __init__(self):
        self.attr0 = self.attr1 = 1

    @cachedjit
    def myfunc(self, arg):
        return self.attr1 + self.attr0 + arg

    def check(self):
        assert self.myfunc(1) == 3
