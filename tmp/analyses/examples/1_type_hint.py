
import transonic as ts
from transonic import Type, NDim, Array, Union

import numpy as np
import skimage

T = Type(int, np.complex128)

dim = 2
dim += 1

N = NDim(1, dim)

A = Array[T, N]
A1 = Array[np.float32, N + 1]

A3d = Array[np.float32, "3d"]
N1 = NDim(4, 5)
N1 = NDim(4, 5)

T = Type(int, np.complex128)

a_type_var = "hello"
myconst = 0

cdict = skimage.color.color_dict

@ts.boost
def compute(a: A, b: A, c: T, d: Union[A, A1], e: str):
    print(e)
    tmp = a + b + myconst
    return tmp
