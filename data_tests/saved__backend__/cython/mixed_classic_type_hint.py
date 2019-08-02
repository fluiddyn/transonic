import numpy as np


def func(a, b):
    return (a * np.log(b)).max()


def func1(a, b):
    return a * np.cos(b)


# pythran export __transonic__
__transonic__ = ("0.2.4",)
