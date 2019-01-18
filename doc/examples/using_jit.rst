Cached Just-In-Time compilation
===============================

With Transonic, one can use the Ahead-Of-Time compiler Pythran in a
Just-In-Time mode. It is really the **easiest way to speedup a function with
Pythran**, just by adding a decorator! And it works also in notebooks!

It is a "work in progress" so the API is not great, but it is a good start!

.. literalinclude:: using_jit.py

In the long terms, we won't need the :code:`#pythran import ...` and
:code:`@include`...

Note that it can be very convenient to use type hints **and**
:code:`@jit` in order to avoid multiple warmup periods:

.. literalinclude:: using_jit_diff_types.py

If the environment variable :code:`TRANSONIC_COMPILE_AT_IMPORT` is set, transonic
compiles at import time the functions with type hints.

Comparison Numba vs Transonic
--------------------------------

Code taken from this `blog post
<https://flothesof.github.io/optimizing-python-code-numpy-cython-pythran-numba.html>`_
by Florian LE BOURDAIS.

.. literalinclude:: perf_numba.py

The warmup is much longer for Transonic but remember that it is a cached JIT
so it is an issue only for the first call of the function. When we reimport the
module, there is no warmup.

Then we see that **Pythran is very good to optimize high-level NumPy code!** In
contrast, (with my setup and on my computer) Numba has not been able to
optimize this function.

However, Numba is good to speedup the code with loops, but even with this code,
it is still slightly slower than Pythran with the high-level NumPy code.
