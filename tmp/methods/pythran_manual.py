import numpy as np

# pythran export __for_method__Transmitter____call__(float, float[:])
# pythran export __for_method__Transmitter____call__(float, int[:])
# pythran export __for_method__Transmitter____call__(float, float[:, :])
# pythran export __for_method__Transmitter____call__(float, int[:, :])


def __for_method__Transmitter____call__(self_freq, inp):
    "My docstring"
    print("__for_method...")
    return inp * np.exp(((np.arange(len(inp)) * self_freq) * 1j))


# pythran export __code_new_method__Transmitter____call__

__code_new_method__Transmitter____call__ = """

def new_method(self, inp):
    print("new_method")
    return backend_func(self.freq, inp)

"""
