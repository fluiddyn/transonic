import numpy as np

# pythran import numpy as np

# pythran blabla

from transonic import Transonic

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
            #     float[][] a, b;
            #     int n
            # ) -> result
            # blabla

            # blibli

            # pythran block (
            #     float[][][] a, b;
            #     int n
            # ) -> result
            result = np.zeros_like(a)
            for _ in range(n):
                result += a ** 2 + b ** 3

        a = result

        if fp.is_transpiled:
            result = fp.use_block("block1")
        else:
            # pythran block (
            #     float[][] a, b;
            #     int n
            # ) -> (result)
            # blabla

            # blibli

            # pythran block (
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

    print("(is_transpiled, is_compiling, is_compiled)", (fp.is_transpiled, fp.is_compiling, fp.is_compiled))

    if fp.is_transpiled:
        ret = obj.compute(10)
        assert np.allclose(ret, ret0), (ret - ret0)
        fp.is_transpiled = False
        ret1 = obj.compute(10)
        fp.is_transpiled = True
        assert np.allclose(ret, ret1), (ret - ret1)
        print("allclose OK")
