import numpy as np

from fluiddyn.util import mpi

from fluidpythran import pythran_def

# pythran import numpy as np

# pythran def func(float[][], float[][])
# pythran def func(int[][], float[][])


@pythran_def
def func(a: float, b: float):
    return (a * np.log(b)).max()


@pythran_def
def func1(a: int, b: float):
    return a * np.cos(b)
