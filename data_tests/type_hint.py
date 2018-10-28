
import numpy as np
import fluidpythran as fp


T = fp.TypeVar("T")
T1 = fp.TypeVar("T1")
D = fp.DimVar("D")

A = fp.Array[T, D]
A1 = fp.Array[T1, D + 1]

@fp.pythran_def
def compute(a: A, b: A1, c: T, d: A, e: str):
    print(e)
    tmp = a + b
    return tmp


for dtype in [int, np.complex128]:
    for ndim in [2, 3]:
        fp.make_signature(compute, T=dtype, D=ndim, T1=float)
