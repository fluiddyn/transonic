import numpy as np


def func(a, b):
    return (a * np.log(b)).max()


def func1(a, b):
    return a * np.cos(b)


def __transonic__():
    return "0.7.1"
