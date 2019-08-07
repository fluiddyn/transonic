import numpy as np

# pythran export __for_method__Transmitter____call__(float[:, :], float64, float64[:])


def __for_method__Transmitter____call__(self_arr, self_freq, inp):
    "My docstring"
    return ((inp * np.exp(((np.arange(len(inp)) * self_freq) * 1j))), self_arr)


# pythran export __code_new_method__Transmitter____call__

__code_new_method__Transmitter____call__ = """

def new_method(self, inp):
    return backend_func(self.arr, self.freq, inp)

"""

# pythran export __transonic__
__transonic__ = ("0.2.1",)
