"""
Serge talked about @cachedjit

It's indeed a good idea.

With "# pythran import" and @used_by_cachedjit the implementation should not be
too complicated.

- At import time, we can create one .py file per cachedjit function.

- At run time, we can create (and complete when needed) a corresponding
  .pythran file with signature(s).

  The cachedjit decorator will have to:

  * at the first call, get the types, create the .pythran file and call
    Pythran.

  * then, try to call the pythran function and if it fails with
    a Pythran type error, correct the .pythran file and recompile.

Note: it's going to be very slow the first time and each time there is a
Pythran type error. Is it better to stop the computation during the
compilation? We could also use the Python function during the compilation and
use the Pythran function once it is ready.

Note: it should also be possible to use type hints to get at the first
compilation more than one signature.

"""

import numpy as np

# pythran import numpy as numpy


from fluidpythran import cachedjit, used_by_cachedjit

""" We could of course avoid this by analyzing the code of the cachedjit
function. For a first implementation, it is simpler to have thus decorator."""


@used_by_cachedjit("func1")
def func0(a, b):
    return a + b


@cachedjit
def func1(a, b):
    return np.exp(a) * b * func0(a, b)
