
import numpy as np
# transonic import numpy as np


class Transmitter():

    freq: float

    def __init__(self, freq):
        self.freq = float(freq)

    def __call__(self, inp: "float[]"):
        """My docstring"""
        return inp * np.exp(np.arange(len(inp))*self.freq*1j)
