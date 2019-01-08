import numpy as np
import transonic as fp
from transonic import Type, NDim, Array

T = Type("T")
N = NDim("N")

A = Array[T, N]
A1 = Array[np.int8, N + 1]


@fp.boost
def compute(a: A, b: A, c: T, d: A1, e: str):
    print(e)
    tmp = a + b
    return tmp


for dtype in [int, np.complex128]:
    for ndim in [1, 3]:
        fp.make_signature(compute, T=dtype, N=ndim)


if __name__ == "__main__":
    print(__name__)

    shape = [2]

    a = b = np.zeros(shape, dtype=int)
    d = np.zeros(shape + [2], dtype=np.int8)

    compute(a, b, 5, d, "hello")
