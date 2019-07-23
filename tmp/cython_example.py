from transonic import boost
import numpy as np

@boost
def func(n : int, m : int):
    return np.add(1,n)

