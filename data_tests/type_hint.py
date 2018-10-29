import numpy as np
import fluidpythran as fp
from fluidpythran import TypeVar, NDimVar, Array

T = TypeVar("T")
T1 = TypeVar("T1")
N = NDimVar("N")

A = Array[T, N]
A1 = Array[T1, N + 1]

# for coverage
assert repr(N - 1) == "N - 1"
print(repr(A1))


@fp.pythran_def
def compute(a: A, b: A1, c: T, d: A, e: str):
    print(e)
    tmp = a + b
    return tmp


for dtype in [int, np.complex128]:
    for ndim in [1, 3]:
        fp.make_signature(compute, T=dtype, N=ndim, T1=float)


if __name__ == "__main__":
    print(__name__)
