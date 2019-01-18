"""
See https://bitbucket.org/fluiddyn/fluidpythran/issues/7/

We can use the decorator transonic.include but here we don't use it bacause
it should not be difficult to detect that `func` uses `mylog`.

"""
import numpy as np

from transonic import boost

# transonic import numpy as np


def mylog(arr):
    return np.log(arr)


@boost
def func(a: float, b: float):
    return (a * mylog(b)).max()
