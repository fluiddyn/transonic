

import fluidpythran as fp


class MyClass:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def compute(self, n):

        a = self.a
        b = self.b

        if fp.is_pythranized():
            result = fp.use_pythranized_block("block0")
        else:
            # pythran block (
            #     float[][] a, b;
            #     int n
            # ) -> result
            # silly comment

            # another comment here

            # pythran block (
            #     float[][][] a, b;
            #     int n
            # ) -> result
            result = 0.0
            for _ in range(n):
                result += a**2 + b**3

        return result
