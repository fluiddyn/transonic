
import numpy as np

from fluidpythran import boost

# FLUIDPYTHRAN_NO_IMPORT

# pythran import numpy as np

# pythran def func(
#  float[][],
#  float[][]
# )
# pythran def func(int[][], float[][])


@boost
def func(a, b):
    return (a * np.log(b)).max()
