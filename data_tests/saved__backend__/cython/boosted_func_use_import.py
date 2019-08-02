import numpy as np
from exterior_import_boost import func_import


def func(a, b):
    return (a * np.log(b)).max() + func_import()


# pythran export __transonic__
__transonic__ = ("0.2.4",)
