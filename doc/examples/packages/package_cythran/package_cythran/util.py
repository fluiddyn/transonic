import matplotlib.pyplot as plt
import numpy as np

from transonic import Type, boost, set_backend_for_this_module

set_backend_for_this_module("cython")

T = Type(float, int)


@boost
def func(a: T):
    b = 1
    return a * np.sin(b)
