import numpy as np
from local_module import multiply

from transonic import boost

# transonic def func(float[][], float[][])
# transonic def func(int[][], float[][])


def my_log(b):
    return np.log(b)


@boost
def func(a, b):
    c = multiply(a,b)
    return (c * my_log(b)).max()
