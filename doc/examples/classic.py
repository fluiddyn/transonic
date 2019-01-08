import numpy as np

# don't import any random modules in a Pythran file. Here, no problem!
from fluiddyn.util import mpi

from transonic import boost

# TRANSONIC_NO_IMPORT

# pythran import numpy as np

# pythran def func(float[][], float[][])
# pythran def func(int[][], float[][])


@boost
def func(a, b):
    return (a * np.log(b)).max()


if __name__ == "__main__":

    n0, n1 = 100, 200
    a0 = np.random.rand(n0, n1)
    a1 = np.random.rand(n0, n1)

    result = func(a0, a1)
    if mpi.nb_proc > 1:
        result = mpi.comm.allreduce(result, op=mpi.MPI.MAX)
    mpi.printby0(result)

    a0 = (1000 * a0).astype(int)
    result = func(a0, a1)
    if mpi.nb_proc > 1:
        result = mpi.comm.allreduce(result, op=mpi.MPI.MAX)
    mpi.printby0(result)
