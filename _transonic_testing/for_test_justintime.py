import numpy as np

from transonic import jit, boost
from transonic.mpi import Path


def func0(a):
    return 2 * a


def func():
    return 1


func0_jitted = jit(func0)


@jit
def func1(a: "int[][] or float[]", l: "int list"):
    tmp = np.exp(sum(l))
    result = tmp * a * func0(a) + func()
    return result


@jit
def func_identity(a):
    return a


# weird but done on purpose for a better coverage
Path(__file__).touch()


@jit()
def func_identity(a):
    return a


@jit
def func_dict(d: "str: float dict"):
    return d.popitem()


@jit
def fib(n: int):
    """fibonacci"""
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


@jit
def use_fib():
    return [fib(n) for n in [1, 3, 5]]


@boost
class MyClass:
    def __init__(self):
        self.attr0 = self.attr1 = 1

    @jit()
    def myfunc(self, arg):
        return self.attr1 + self.attr0 + np.abs(arg)

    @jit
    def myfunc1(self):
        return self.attr0

    def check(self):
        assert self.myfunc(1) == 3


# FIXME support multilevel imported jitted function call in a jitted function
from .for_test_exterior_import_jit import foo, func_import, func_import2
from numpy import pi

const = 1

jitted_func_import = jit(func_import)
jitted_func_import2 = jit(func_import2)


@jit
def main(add: int):
    return (
        add
        + foo
        + pi
        - pi
        - jitted_func_import()
        + func_import2()
        + func0_jitted(1 / 2)
        + const
    )


@boost
class MyClass2:
    def __init__(self):
        self.attr0 = self.attr1 = 1

    @jit()
    def myfunc(self, arg):
        return self.attr1 + self.attr0 + np.abs(arg) + func_import()

    def check(self):
        assert self.myfunc(1) == 4
