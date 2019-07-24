
import numpy as np
import matplotlib.pyplot as plt
import h5netcdf

from transonic import boost, Type


T = Type(float, int)

@boost
def func(a: T):
    b = 1
    return a * np.sin(b)
