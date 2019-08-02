import numpy as np
from __ext__func__exterior_import_boost import func_import


# pythran export func(float[][], float[][])
# pythran export func(int[][], float[][])
def func(a, b):
    return (a * np.log(b)).max() + func_import()


# pythran export __transonic__
__transonic__ = ("0.2.3",)
