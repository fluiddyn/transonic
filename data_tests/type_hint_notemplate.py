import numpy as np
import fluidpythran as fp
from fluidpythran import TypeVar, NDimVar, Array

T = TypeVar("T", int, np.complex128)
N = NDimVar("N", 1, 3)

A = Array[T, N]
A1 = Array[np.float32, N + 1]


@fp.pythran_def
def compute(a: A, b: A, c: T, d: A1, e: str):
    print(e)
    tmp = a + b
    return tmp
