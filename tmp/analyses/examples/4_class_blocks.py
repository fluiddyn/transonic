import numpy as np

from transonic import Transonic

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
            # transonic block (
            #     float[][] a, b;
            #     int n
            # ) -> result
            # blabla

            # blibli

            # transonic block (
            #     float[][][] a, b;
            #     int n
            # ) -> result
            result = np.zeros_like(a)
            for _ in range(n):
                result += a ** 2 + b ** 3

        a = result

        if ts.is_transpiled:
            result = ts.use_block("block1")
        else:
            # transonic block (
            #     float[][] a, b;
            #     int n
            # ) -> (result)
            # blabla

            # blibli

            # transonic block (
            #     float[][][] a, b;
            #     int n
            # ) -> (result)
            result = np.zeros_like(a)
            for _ in range(n):
                result += a ** 2 + b ** 3

        return result


if __name__ == "__main__":

    shape = 2, 2
    a = np.random.rand(*shape)
    b = np.random.rand(*shape)

    obj = MyClass(a, b)

    ret0 = obj.compute(10)

    print("(is_transpiled, is_compiling, is_compiled)", (ts.is_transpiled, ts.is_compiling, ts.is_compiled))

    if ts.is_transpiled:
        ret = obj.compute(10)
        assert np.allclose(ret, ret0), (ret - ret0)
        ts.is_transpiled = False
        ret1 = obj.compute(10)
        ts.is_transpiled = True
        assert np.allclose(ret, ret1), (ret - ret1)
        print("allclose OK")
