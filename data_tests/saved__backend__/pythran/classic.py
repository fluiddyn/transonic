import numpy as np


def func(a, b):
    return (a * np.log(b)).max()


__transonic__ = ("0.3.0",)
