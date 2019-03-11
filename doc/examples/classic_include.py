import numpy as np

from transonic import boost

# transonic def func(float[][], float[][])
# transonic def func(int[][], float[][])


def my_log(b):
    return np.log(b)


@boost
def func(a, b):
    return (a * my_log(b)).max()
