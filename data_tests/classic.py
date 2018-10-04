
import numpy as np

from fluidpythran import FluidPythran

fp = FluidPythran()

# pythran import numpy as np

# pythran def func(
#  float[][],
#  float[][]
# )
# pythran def func(int[][], float[][])


@fp.pythranize
def func(a, b):
    return (a * np.log(b)).max()
