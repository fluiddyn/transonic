import numpy as np
from __ext__func__exterior_import_boost import func_import


def func(a, b):
    return (a * np.log(b)).max() + func_import()


def __transonic__():
    return "0.7.1"
