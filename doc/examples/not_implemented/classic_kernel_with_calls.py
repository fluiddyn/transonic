import numpy as np

from fluidpythran import pythran_def

# pythran import numpy as np


def mylog(arr):
    return np.log(arr)

# pythran def func(float[][], float[][])
# pythran def func(int[][], float[][])


@pythran_def
def func(a, b):
    return (a * mylog(b)).max()