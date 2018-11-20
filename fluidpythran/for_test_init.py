import numpy as np

# pythran import numpy as np

from fluidpythran import FluidPythran, pythran_def


# pythran def func(int, float)


@pythran_def
def func(a, b):
    return a + b


# pythran def func2(int, float)


@pythran_def
def func2(a, b):
    return a - b


fp = FluidPythran()


def func1(a, b):
    n = 10

    if fp.is_transpiled:
        result = fp.use_pythranized_block("block0")
    else:
        # pythran block (
        #     float a, b;
        #     int n
        # ) -> (result, a)
        # blabla

        result = 0.
        for _ in range(n):
            result += a ** 2 + b ** 3
