import numpy as np

# pythran export __method__Transmitter____call__(float, float[])


def __for_method__Transmitter____call__(self_freq, inp):
    return inp * np.exp(np.arange(len(inp))*self_freq*1j)
