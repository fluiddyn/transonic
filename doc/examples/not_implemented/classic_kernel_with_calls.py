import numpy as np

from transonic import boost

# transonic import numpy as np


def mylog(arr):
    return np.log(arr)

# transonic def func(float[][], float[][])
# transonic def func(int[][], float[][])


@boost
def func(a, b):
    return (a * mylog(b)).max()