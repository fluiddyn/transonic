import numpy as np

from transonic import boost

type_ = float


@boost
class Transmitter:

    freq: type_

    def __init__(self, freq):
        self.freq = float(freq)

    @boost
    def __call__(self, inp: "float[]", arg_default: int = 1):
        """My docstring"""
        return inp * np.exp(np.arange(len(inp)) * self.freq * 1j)


if __name__ == "__main__":
    inp = np.ones(2)
    freq = 1.0
    trans = Transmitter(freq)

    def for_check(freq, inp):
        return inp * np.exp(np.arange(len(inp)) * freq * 1j)

    assert np.allclose(trans(inp), for_check(freq, inp))
