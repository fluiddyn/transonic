import numpy as np
import fluidpythran as fp

T = fp.TypeVar("T")
T1 = fp.TypeVar("T1")
N = fp.NDimVar("N")

A = fp.Array[T, N]
A1 = fp.Array[T1, N + 1]


@fp.pythran_def
def compute(a: A, b: A, c: T, d: A1, e: str):
    print(e)
    tmp = a + b
    return tmp


for dtype in [int, np.complex128]:
    for ndim in [1, 3]:
        fp.make_signature(compute, T=dtype, N=ndim, T1=float)


if __name__ == "__main__":
    print(__name__)

    shape = [2]

    a = b = np.zeros(shape, dtype=int)
    d = np.zeros(shape + [2], dtype=float)

    compute(a, b, 5, d, "hello")
