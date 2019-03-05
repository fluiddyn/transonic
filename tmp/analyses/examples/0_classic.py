import numpy as np

from transonic import boost
import transonic as ts

myconst0 = 0
myconst1 = 2*myconst0

# transonic def func(
#  float[][],
#  float[][]
# )
# transonic def func(int[][], float[][])


@boost
def func(a, b):
    return myconst1 * (a * np.log(b)).max()


# transonic def func1(int, float)


@ts.boost
def func1(a, b):
    return (a * np.cos(b)).max()


@boost
class Foo:
    @ts.boost
    def meth_foo(self):
        return func1(0, 1)


@ts.boost
class Bar:
    @boost
    def meth_bar(self):
        pass
