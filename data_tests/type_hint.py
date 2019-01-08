import numpy as np
import transonic as fp
from transonic import Type, NDim, Array

T = Type("T")
T1 = Type("T1")
N = NDim("N")

A = Array[T, N]
A1 = Array[T1, N + 1]

# for coverage
assert repr(N - 1) == "N - 1"
print(repr(A1))


@fp.boost
def compute(a: A, b: A1, c: T, d: A, e: str):
    print(e)
    tmp = a + b
    return tmp


for dtype in [int, np.complex128]:
    for ndim in [1, 3]:
        fp.make_signature(compute, T=dtype, N=ndim, T1=float)


if __name__ == "__main__":
    print(__name__)
