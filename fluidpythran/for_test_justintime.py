
import numpy as np

# pythran import numpy as np

from fluidpythran import cachedjit, used_by_cachedjit
from .mpi import Path


@used_by_cachedjit("func1")
def func0(a):
    return 2 * a


@used_by_cachedjit("func1")
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
