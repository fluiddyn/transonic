import numpy as np

# pythran export func(float[][], float[][])
# pythran export func(int[][], float[][])
def func(a, b):
    return (a * np.log(b)).max()


# pythran export __transonic__
__transonic__ = ("0.2.1",)
