import numpy as np
import fluidpythran as fp
from fluidpythran import Type, NDim, Array

T = Type(int, np.complex128)
N = NDim(1, 3)

A = Array[T, N]
A1 = Array[np.float32, N + 1]

A3d = Array[np.float32, "3d"]
N1 = NDim(4, 5)
N1 = NDim(4, 5)

T = Type(int, np.complex128)


@fp.boost
def compute(a: A, b: A, c: T, d: A1, e: str):
    print(e)
    tmp = a + b
    return tmp
