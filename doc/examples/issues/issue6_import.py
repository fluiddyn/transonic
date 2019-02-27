"""
See https://bitbucket.org/fluiddyn/fluidpythran/issues/6/

Here, the function uses np (numpy), but it should of course work for all
packages.

Related question: do we support usage of global variables in "boosted"
functions?

"""
import numpy as np

from transonic import boost

# this one has nothing to do with my_constant used in func
my_constant = 10

# this code produces my_constant used in func
values = [2, 3, 4]
my_constant = len(values)


@boost
def func(a: float, b: float):

    c = a + b + values[0]
    return (a * np.log(c)).max() * my_constant


if __name__ == "__main__":
    result1 = func(1.0, 1.0)
    result2 = func(2.0, 2.0)
