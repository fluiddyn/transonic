from fluidpythran import pythran_class

import numpy as np


@pythran_class
class MyClass:
    # pythran class (
    #     int[] or float[]: arr0, arr1;
    #     float[][]: arr2
    # )

    def __init__(self, n, dtype=int):
        self.arr0 = np.zeros(n, dtype=dtype)
        self.arr1 = np.zeros(n, dtype=dtype)
        self.arr2 = np.zeros(n)

    # pythran def compute(object, float)

    def compute(self, alpha):
        tmp = (self.arr0 + self.arr1).mean()
        return tmp ** alpha * self.arr2
