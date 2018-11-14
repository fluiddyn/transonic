import numpy as np


# pythran import numpy as numpy

from fluidpythran import cachedjit, used_by_cachedjit


@used_by_cachedjit("func1")
def func0(a, b):
    return a + b


@cachedjit
def func1(a, b):
    return np.exp(a) * b * func0(a, b)


@cachedjit()
def func2(a):
    return a
