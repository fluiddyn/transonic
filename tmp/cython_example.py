from transonic import boost 
import numpy as np

@boost(backend = "cython")
def func(n : int, m : int):
    return np.add(1,n)

