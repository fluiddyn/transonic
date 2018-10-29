import numpy as np
import fluidpythran as fp

T = fp.TypeVar("T")
T1 = fp.TypeVar("T1")
N = fp.NDimVar("N")

A = fp.Array[T, N]
A1 = fp.Array[T1, N + 1]

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
