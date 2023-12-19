import numpy as np

from transonic import boost, Array

A = Array[float, "2d"]


@boost
class Transmitter:
    freq: float
    arr: A

    def __init__(self, freq):
        self.freq = float(freq)
        self.arr = np.ones((2, 2))

    @boost
    def __call__(self, inp: "float[]"):
        """My docstring"""
        return inp * np.exp(np.arange(len(inp)) * self.freq * 1j), self.arr


if __name__ == "__main__":
    inp = np.ones(2)
    freq = 1.0
    trans = Transmitter(freq)

    def for_check(freq, inp):
        return inp * np.exp(np.arange(len(inp)) * freq * 1j)

    assert np.allclose(trans(inp), for_check(freq, inp))
