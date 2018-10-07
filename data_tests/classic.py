
import numpy as np

from fluidpythran import pythran_def

# pythran import numpy as np

# pythran def func(
#  float[][],
#  float[][]
# )
# pythran def func(int[][], float[][])


@pythran_def
def func(a, b):
    return (a * np.log(b)).max()
