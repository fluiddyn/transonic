


import numpy as np

# pythran import numpy as np


from transonic import Transonic, Type, NDim, Array

T = Type(float, complex)
N = NDim(1, 2)
A = Array[T, N]
A1 = Array[T, N + 1]

fp = Transonic()


class MyClass:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def compute(self, n):

        a = self.a
        b = self.b

        if fp.is_transpiled:
            result = fp.use_block("block0")
        else:
            # pythran block (
            #     A a; A1 b;
            #     int n
            # ) -> result

            # pythran block (
            #     int[:] a, b;
            #     float n
            # ) -> result

            result = a ** 2 + b.mean() ** 3 + n

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
