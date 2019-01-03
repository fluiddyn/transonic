"""
See https://bitbucket.org/fluiddyn/fluidpythran/issues/6/

Here, the function uses np (numpy), but it should of course work for all
packages.

Related question: do we support usage of global variables in "boosted"
functions?

"""
import numpy as np

from fluidpythran import boost


@boost
def func(a: float, b: float):
    return (a * np.log(b)).max()
