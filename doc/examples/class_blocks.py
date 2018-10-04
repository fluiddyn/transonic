
import numpy as np

# pythran import numpy as np


from fluidpythran import FluidPythran

fp = FluidPythran()


class MyClass:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def compute(self, n):

        a = self.a
        b = self.b

        if fp.is_pythranized:
            result = fp.use_pythranized_block("block0")
        else:
            # pythran block (
            #     float[][] a, b;
            #     int n
            # ) -> result
            # pythran block (
            #     float[][][] a, b;
            #     int n
            # ) -> result
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

    if fp.is_pythranized:
        ret = obj.compute(10)
        fp.is_pythranized = False
        ret1 = obj.compute(10)
        fp.is_pythranized = True
        assert np.allclose(ret, ret1)
        print("allclose OK")
