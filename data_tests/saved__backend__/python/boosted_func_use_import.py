import numpy as np
from exterior_import_boost import func_import


def func(a, b):
    return (a * np.log(b)).max() + func_import()


__transonic__ = ("0.3.0.post0",)
