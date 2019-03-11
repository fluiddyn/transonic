import numpy as np

from transonic import boost

# transonic def func(
#  float[][],
#  float[][]
# )
# transonic def func(int[][], float[][])


@boost
def func(a, b):
    return (a * np.log(b)).max()
