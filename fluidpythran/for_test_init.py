import numpy as np

# pythran import numpy as np

from fluidpythran import FluidPythran, boost, include, Array, Union


# pythran def func(int, float)


@boost
def func(a, b):
    return a + b


@include
def func_tmp(arg):
    return arg ** 2


A = Union[int, Array[int, "1d"]]


@boost
def func2(a: A, b: float):
    return a - func_tmp(b)


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

        result = 0.0
        for _ in range(n):
            result += a ** 2 + b ** 3


@boost
class Transmitter:

    freq: float

    def __init__(self, freq):
        self.freq = float(freq)

    @boost
    def __call__(self, inp: "float[]"):
        """My docstring"""
        return inp * np.exp(np.arange(len(inp)) * self.freq * 1j)

    @boost
    def other_func(self):
        return 2 * self.freq


def check_class():
    inp = np.ones(2)
    freq = 1.0
    trans = Transmitter(freq)

    def for_check(freq, inp):
        return inp * np.exp(np.arange(len(inp)) * freq * 1j)

    assert np.allclose(trans(inp), for_check(freq, inp))
    assert trans.other_func() == 2 * freq


if __name__ == "__main__":
    check_class()
