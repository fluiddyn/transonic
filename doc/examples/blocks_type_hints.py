import numpy as np
# pythran import numpy as np

from fluidpythran import FluidPythran, Type, NDim, Array

T = Type(float, complex)
N = NDim(2, 3)
A = Array[T, N]
A1 = Array[T, N + 1]

fp = FluidPythran()


class MyClass:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def compute(self, n):

        a = self.a
        b = self.b

        if fp.is_transpiled:
            result = fp.use_pythranized_block("block0")
        else:
            # pythran block (A a, b; A1 c; int n) -> result
            # pythran block (int a, b, c; float n) -> result

            result = np.zeros_like(a)
            for _ in range(n):
                result += a ** 2 + b ** 3

        return result


if __name__ == "__main__":

    shape = 100, 100
    a = np.random.rand(*shape)
    b = np.random.rand(*shape)

    obj = MyClass(a, b)

    obj.compute(10)

    if fp.is_transpiled:
        ret = obj.compute(10)
        fp.is_transpiled = False
        ret1 = obj.compute(10)
        fp.is_transpiled = True
        assert np.allclose(ret, ret1)
        print("allclose OK")
