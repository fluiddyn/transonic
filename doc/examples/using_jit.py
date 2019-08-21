import numpy as np

from transonic import jit


def func0(a, b):
    return a + b


@jit
def func1(a: int, b: int):
    print("b", b)
    return np.exp(a) * b * func0(a, b)


if __name__ == "__main__":

    from time import sleep

    a = b = np.zeros([2, 3])

    for i in range(20):
        print(f"{i}, call with arrays")
        func1(a, b)
        print(f"{i}, call with numbers")
        func1(1, 1.5)
        sleep(1)
