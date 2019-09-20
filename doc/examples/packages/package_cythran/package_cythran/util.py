
import numpy as np
import matplotlib.pyplot as plt

from transonic import boost, Type, set_backend_for_this_module

set_backend_for_this_module("cython")

T = Type(float, int)

@boost
def func(a: T):
    b = 1
    return a * np.sin(b)
