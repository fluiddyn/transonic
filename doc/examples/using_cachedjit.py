import numpy as np
# pythran import numpy as np

from fluidpythran import cachedjit, used_by_cachedjit

@used_by_cachedjit("func1")
def func0(a, b):
    return a + b

@cachedjit()
def func1(a, b):
    return np.exp(a) * b * func0(a, b)

if __name__ == "__main__":

    from time import sleep

    a = b = np.zeros([2, 3])

    for _ in range(40):
        print(_)
        func1(a, b)
        sleep(1)
