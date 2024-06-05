import matplotlib.pyplot as plt
import numpy as np

from transonic import Type, boost

T = Type(float, int)


@boost
def func(a: T):
    b = 1
    return a * np.sin(b)
