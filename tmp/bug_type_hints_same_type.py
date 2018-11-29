
import numpy as np

from fluidpythran import FluidPythran, Type, NDim, Array

fp = FluidPythran()

T = Type(np.complex128)
N = NDim(3)
A = Array[T, N]

T = Type(np.float64, np.complex128)
A1 = Array[T, N]


def func(a, b):

    if fp.is_transpiled:
        fp.use_pythranized_block("rk2_step0")
    else:
        # pythran block (
        #     A a;
        #     A1 b
        # )

        a.sum() + b
