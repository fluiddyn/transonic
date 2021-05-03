# __protected__ from numba import njit
import numpy as np

# __protected__ @njit(cache=True, fastmath=True)


def __for_method__Transmitter____call__(self_arr, self_freq, inp):
    """My docstring"""
    return (inp * np.exp(np.arange(len(inp)) * self_freq * 1j), self_arr)


__code_new_method__Transmitter____call__ = "\n\ndef new_method(self, inp):\n    return backend_func(self.arr, self.freq, inp)\n\n"
__transonic__ = ("0.4.7",)
