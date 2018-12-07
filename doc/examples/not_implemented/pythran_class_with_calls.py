"""
With classes, we have a problem with heritage. Note that for standard functions
(like sum_arrays), we actually also have the problem with monkey patching.

We can just say that monkey patching of `sum_arrays` is not supported (so that
`sum_arrays` can be treated as a Pythran function, and potentially inlined) but
for class, we really want to support heritage (like in MyClassChild) so we
would need to replace `compute` by a Python method calling Pythran functions
and Python methods (which themselves call Pythran functions).

The mechanism needed for `compute` is much more complicated than the simple
case in `pythran_class.py` and more complicated than what is needed for
`compute1` (which is actually similar to [issue
#7](https://bitbucket.org/fluiddyn/fluidpythran/issues/7/support-kernels-with-function-calls)).

"""

from fluidpythran import Type, NDim, Array, boost

import numpy as np


T = Type(int, np.float64)
N = NDim(1)

A1 = Array[T, N]
A2 = Array[float, N + 1]


def sum_arrays(arr0, arr1):
    return arr0 + arr1


class MyClass:

    arr0: A1
    arr1: A1
    arr2: A2

    def __init__(self, n, dtype=int):
        self.arr0 = np.zeros(n, dtype=dtype)
        self.arr1 = np.zeros(n, dtype=dtype)
        self.arr2 = np.zeros(n)

    @boost
    def compute(self, alpha: float):
        tmp = self.sum_arrays().mean()
        return tmp ** alpha * self.arr2

    def sum_arrays(self):
        return self.arr0 + self.arr1

    @boost
    def compute1(self, alpha: float):
        tmp = sum_arrays(self.arr0, self.arr1).mean()
        return tmp ** alpha * self.arr2


class MyClassChild(MyClass):
    def sum_arrays(self):
        return 2 * self.arr0 + self.arr1
