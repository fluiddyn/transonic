import numpy as np

from transonic import boost
from exterior_import_boost import func_import

# from transonic.exterior_import_jit import func_import
# transonic def func(
#  float[][],
#  float[][]
# )
# transonic def func(int[][], float[][])


@boost
def func(a, b):
    return (a * np.log(b)).max() + func_import()
