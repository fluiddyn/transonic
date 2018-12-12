import numpy as np

from fluidpythran import boost, include

# pythran import numpy as np

# pythran def func(float[][], float[][])
# pythran def func(int[][], float[][])


@include
def my_log(b):
    return np.log(b)


@boost
def func(a, b):
    return (a * my_log(b)).max()
