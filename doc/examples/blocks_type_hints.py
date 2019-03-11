import numpy as np

from transonic import Transonic, Type, NDim, Array

T = Type(float, complex)
N = NDim(2, 3)
A = Array[T, N]
A1 = Array[T, N + 1]

ts = Transonic()


class MyClass:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def compute(self, n):

        a = self.a
        b = self.b

        if ts.is_transpiled:
            result = ts.use_block("block0")
        else:
            # transonic block (A a, b; A1 c; int n)
            # transonic block (int a, b, c; float n)

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

    if ts.is_transpiled:
        ret = obj.compute(10)
        ts.is_transpiled = False
        ret1 = obj.compute(10)
        ts.is_transpiled = True
        assert np.allclose(ret, ret1)
        print("allclose OK")
