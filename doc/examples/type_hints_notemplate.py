import numpy as np
from transonic import Type, NDim, Array, boost

T = Type(int, np.complex128)
N = NDim(1, 3)

A = Array[T, N]
A1 = Array[np.float32, N + 1]


@boost
def compute(a: A, b: A, c: T, d: A1, e: str):
    print(e)
    tmp = a + b
    return tmp
