import numpy as np

from transonic import boost, include

# transonic import numpy as np

# transonic def func(float[][], float[][])
# transonic def func(int[][], float[][])


@include
def my_log(b):
    return np.log(b)


@boost
def func(a, b):
    return (a * my_log(b)).max()
