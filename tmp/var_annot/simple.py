import numpy as np

from transonic import Type, NDim, Array, boost

T = Type(np.float64, np.complex128)
N = NDim(1)
A = Array[T, N]


@boost
def func(a: A):
    i: int
    n: int = a.shape[0]

    for i in range(n):
        a[i] = a[i] + 1.
