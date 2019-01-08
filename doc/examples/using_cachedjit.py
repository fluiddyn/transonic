import numpy as np
# pythran import numpy as np

from transonic import cachedjit, include

@include("func1")
def func0(a, b):
    return a + b

@cachedjit()
def func1(a, b):
    return np.exp(a) * b * func0(a, b)

if __name__ == "__main__":

    from time import sleep

    a = b = np.zeros([2, 3])

    for i in range(40):
        print(f"{i}, call with arrays", end=", ")
        func1(a, b)
        print("call with numbers")
        func1(1, 1.)
        sleep(1)
