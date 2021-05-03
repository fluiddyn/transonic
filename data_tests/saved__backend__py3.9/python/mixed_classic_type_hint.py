import numpy as np


def func(a, b):
    return (a * np.log(b)).max()


def func1(a, b):
    return a * np.cos(b)


__transonic__ = ("0.3.0.post0",)
