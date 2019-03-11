import numpy as np

from transonic import jit


def func0(a, b):
    return a + b


@jit
def func1(a, b):
    return np.exp(a) * b * func0(a, b)


if __name__ == "__main__":

    from time import sleep

    a = b = np.zeros([2, 3])

    for i in range(40):
        print(f"{i}, call with arrays", end=", ")
        func1(a, b)
        print("call with numbers")
        func1(1, 1.0)
        sleep(1)
