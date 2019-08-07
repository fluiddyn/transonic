from functools import wraps

import numpy as np

import pythran_manual

code = """

def new_method(self, inp):
    return backend_func(self.freq, inp)

"""


def my_decor(func):
    func_name = func.__name__

    name_backend_func = "__for_method__Transmitter__" + func_name

    backend_func = pythran_manual.__dict__[name_backend_func]

    namespace = {"backend_func": backend_func}
    exec(code, namespace)
    return wraps(func)(namespace["new_method"])


class Transmitter:

    freq: float

    def __init__(self, freq):
        self.freq = float(freq)

    @my_decor
    def __call__(self, inp: "float[]"):
        """My docstring"""
        return inp * np.exp(np.arange(len(inp)) * self.freq * 1j)
