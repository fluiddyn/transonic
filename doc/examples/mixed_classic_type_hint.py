import numpy as np

# don't import skimage in a Pythran file. Here, no problem!
from skimage.filters import sobel

from transonic import boost

# pythran import numpy as np

# pythran def func(float[][], float[][])
# pythran def func(int[][], float[][])


@boost
def func(a: float, b: float):
    return (a * np.log(b)).max()


@boost
def func1(a: int, b: float):
    return a * np.cos(b)
