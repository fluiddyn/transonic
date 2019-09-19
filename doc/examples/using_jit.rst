Cached Just-In-Time compilation
===============================

With Transonic, one can use the Ahead-Of-Time compiler Pythran in a
Just-In-Time mode. It is really the **easiest way to speedup a function with
Pythran**, just by adding a decorator! And it works also in notebooks!

.. literalinclude:: using_jit.py

Note that it can be very convenient to use type hints **and**
:code:`@jit` in order to avoid multiple warmup periods:

.. literalinclude:: using_jit_diff_types.py

If the environment variable :code:`TRANSONIC_COMPILE_AT_IMPORT` is set,
transonic compiles at import time the functions with type hints.

Comparison Numba vs Transonic
--------------------------------

Code taken from this `blog post
<https://flothesof.github.io/optimizing-python-code-numpy-cython-pythran-numba.html>`_
by Florian LE BOURDAIS.

.. literalinclude:: perf_numba.py

which gives:

.. code::

    transonic 0.3.3.post0
    pythran 0.9.3post1
    numba 0.45.1

    laplace_transonic_pythran        : 1.00
    norm = 1.47e-04 s
    laplace_transonic_pythran_loops  : 1.06
    laplace_numba                    : 8.32
    laplace_transonic_numba          : 8.81
    laplace_numba_loops              : 1.02
    laplace_transonic_numba_loops    : 1.05
    laplace_numpy                    : 7.19
    laplace_transonic_python         : 7.21


The warmup is much longer for Transonic-Pythran but remember that it is a
cached JIT so it is an issue only for the first call of the function. When we
reimport the module, there is no warmup.

Then we see that **Pythran is very good to optimize high-level NumPy code!** In
contrast (with my setup and on my computer), Numba has not been able to
optimize this function. However, Numba is good to speedup the code with loops!
