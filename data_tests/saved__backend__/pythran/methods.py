import numpy as np


def __for_method__Transmitter____call__(self_arr, self_freq, inp):
    """My docstring"""
    return (inp * np.exp(np.arange(len(inp)) * self_freq * 1j), self_arr)


def __code_new_method__Transmitter____call__():
    return """

def new_method(self, inp):
    return backend_func(self.arr, self.freq, inp)

"""


def __transonic__():
    return "0.7.1"
