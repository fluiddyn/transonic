
import numpy as np

from transonic import boost

# TRANSONIC_NO_IMPORT

# transonic import numpy as np

# transonic def func(
#  float[][],
#  float[][]
# )
# transonic def func(int[][], float[][])


@boost
def func(a, b):
    return (a * np.log(b)).max()
