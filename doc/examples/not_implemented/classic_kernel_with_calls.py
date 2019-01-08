import numpy as np

from transonic import boost

# pythran import numpy as np


def mylog(arr):
    return np.log(arr)

# pythran def func(float[][], float[][])
# pythran def func(int[][], float[][])


@boost
def func(a, b):
    return (a * mylog(b)).max()