


import numpy as np

from transonic import Transonic, Type, NDim, Array

T = Type(float, complex)
N = NDim(1, 2)
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
            # transonic signature (
            #     A a; A1 b;
            #     float n
            # )

            # transonic signature (
            #     int[:] a, b;
            #     float n
            # )

            result = a ** 2 + b.mean() ** 3 + n

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
