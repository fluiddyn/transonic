import numpy as np

# pythran import numpy as np

from fluidpythran import FluidPythran

fp = FluidPythran()

# pythran def func(int, float)


@fp.pythranize
def func(a, b):
    return a + b


def func1(a, b):
    n = 10

    if fp.is_pythranized:
        result = fp.use_pythranized_block("block0")
    else:
        # pythran block (
        #     float a, b;
        #     int n
        # ) -> (result, a)
        # blabla

        result = np.zeros_like(a)
        for _ in range(n):
            result += a ** 2 + b ** 3
