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

from fluidpythran import pythran_class

import numpy as np

def sum_arrays(arr0, arr1):
    return arr0 + arr1

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
        tmp = self.sum_arrays().mean()
        return tmp ** alpha * self.arr2

    def sum_arrays(self):
        return self.arr0 + self.arr1

    # pythran def compute1(object, float)

    def compute1(self, alpha):
        tmp = sum_arrays(self.arr0, self.arr1).mean()
        return tmp ** alpha * self.arr2


class MyClassChild(MyClass):
    def sum_arrays(self):
        return 2*self.arr0 + self.arr1