
import numpy as np

# pythran import numpy as np


from fluidpythran import pythran_block


class MyClass:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    @pythran_block
    def compute(self, n):

        a = self.a
        b = self.b

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

        # pythran end block

        return result
