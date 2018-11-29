from fluidpythran import Type, NDim, Array, pythran_def

import numpy as np


T = Type(int, np.float64)
N = NDim(1)

A1 = Array[T, N]
A2 = Array[float, N+1]


class MyClass:

    arr0: A1
    arr1: A1
    arr2: A2

    def __init__(self, n, dtype=int):
        self.arr0 = np.zeros(n, dtype=dtype)
        self.arr1 = np.zeros(n, dtype=dtype)
        self.arr2 = np.zeros(n)

    @pythran_def
    def compute(self, alpha: int):
        tmp = (self.arr0 + self.arr1).mean()
        return tmp ** alpha * self.arr2
