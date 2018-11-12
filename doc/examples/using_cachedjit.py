"""
Serge talked about @cachedjit (see https://gist.github.com/serge-sans-paille/28c86d2b33cd561ba5e50081716b2cf4)

It's indeed a good idea.

With "# pythran import" and @used_by_cachedjit the implementation isn't
too complicated.

- At import time, we create one .py file per cachedjit function.

- At run time, we create (and complete when needed) a corresponding
  .pythran file with signature(s).

  The cachedjit decorator:

  * at the first call, get the types, create the .pythran file and call
    Pythran.

  * then, try to call the pythran function and if it fails with
    a Pythran TypeError, correct the .pythran file and recompile.

Note: During the compilation (the "warmup" of the JIT), the Python function is
used.

Note (NotImplemented): it should also be possible to use type hints to get at
the first compilation more than one signature.

"""

    import numpy as np

    # pythran import numpy as numpy


    from fluidpythran import cachedjit, used_by_cachedjit

    """ We could of course avoid this by analyzing the code of the cachedjit
    function. For a first implementation, it is simpler to have thus decorator."""


    @used_by_cachedjit("func1")
    def func0(a, b):
        return a + b


    @cachedjit()
    def func1(a, b):
        return np.exp(a) * b * func0(a, b)


if __name__ == "__main__":

    from time import sleep

    a = b = np.zeros([2, 3])

    for _ in range(40):
        print(_)
        func1(a, b)
        sleep(1)
