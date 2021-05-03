try:
    import cython
except ImportError:
    from transonic_cl import cython

import numpy as np


def __for_method__Transmitter____call__(self_arr, self_freq, inp):
    "My docstring"
    return ((inp * np.exp(((np.arange(len(inp)) * self_freq) * 1j))), self_arr)


__code_new_method__Transmitter____call__ = """

def new_method(self, inp):
    return backend_func(self.arr, self.freq, inp)

"""

__transonic__ = ("0.3.3",)
