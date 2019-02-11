"""
See https://bitbucket.org/fluiddyn/fluidpythran/issues/6/

Here, the function uses np (numpy), but it should of course work for all
packages.

Related question: do we support usage of global variables in "boosted"
functions?

"""
import numpy as np

from transonic import boost

my_constant = 3


@boost
def func(a: float, b: float):

    c = a + b
    return (a * np.log(c)).max() * my_constant


if __name__ == "__main__":
    result1 = func(1., 1.)
    result2 = func(2., 2.)