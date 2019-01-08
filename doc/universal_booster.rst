Big long-term idea: a "universal" Numpy booster
===============================================

It would be very useful to have a pure-Python package similar to Transonic
but able to accelerate Numpy code with different tools (Pythran, Cython, Numba,
Numba with CuPy, PyTorch)...

The idea was first proposed in `issue #21
<https://bitbucket.org/fluiddyn/fluidpythran/issues/21>`_.

First step: refactor the code to split the analysis (Transonic "frontend")
and the production and compilations of Pythran files (a Pythran backend). This
backend should be written as an extension (`issue #32
<https://bitbucket.org/fluiddyn/fluidpythran/issues/32>`_).

Second step: write a Numba backend extension (it should not be too difficult
because we don't have to handle the compilation).
