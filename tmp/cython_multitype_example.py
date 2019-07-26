from transonic import boost, Type
import numpy as np

T = Type(int, float)
T2 = Type(float, complex)

@boost
def func(m : T, n : T2):
    return np.add(1,n)

@boost
def func1(m : T, n : float = 2):
    return np.add(1,n)
