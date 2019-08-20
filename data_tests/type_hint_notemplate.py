from functools import partial

import numpy as np

import transonic as ts
from transonic import Type, NDim, Array, Union

T = Type(int, np.complex128)
N = NDim(1, 3)

A = Array[T, N]
A1 = Array[np.float32, N + 1]

A3d = Array[np.float32, "3d"]
N1 = NDim(4, 5)
N1 = NDim(4, 5)

T = Type(int, np.complex128)


@ts.boost
def compute(a: A, b: A, c: T, d: Union[A, A1], e: str):
    print(e)
    tmp = a + b
    if 1 and 2:
        tmp *= 2
    return tmp


main = partial(lambda x: x, lambda x: x)
