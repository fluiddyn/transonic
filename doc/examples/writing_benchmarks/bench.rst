Writing benchmarks
==================

Comparison Numba vs Pythran (JIT)
---------------------------------

We take this file with only pure-Numpy code from this `blog post
<https://flothesof.github.io/optimizing-python-code-numpy-cython-pythran-numba.html>`_
by Florian LE BOURDAIS.

.. literalinclude:: pure_numpy.py

Our code for a benchmark in JIT mode:

.. literalinclude:: bench_jit.py

gives:

.. code::

    transonic 0.4.0
    pythran 0.9.3post1
    numba 0.45.1

    laplace_transonic_pythran        : 1.00
    norm = 1.44e-04 s
    laplace_transonic_pythran_loops  : 0.94
    laplace_numba                    : 8.82
    laplace_transonic_numba          : 8.80
    laplace_numba_loops              : 0.94
    laplace_transonic_numba_loops    : 0.94
    laplace_numpy                    : 6.94
    laplace_transonic_python         : 7.03


The warmup is much longer for Transonic-Pythran but remember that it is a
cached JIT so it is an issue only for the first call of the function. When we
reimport the module, there is no warmup.

Then we see that **Pythran is very good to optimize high-level NumPy code!** In
contrast (with my setup and on my computer), Numba has not been able to
optimize this function. However, Numba is good to speedup the code with loops!

Note that the Transonic overhead is negligible even for this very small case
(the shape of the image is ``(512, 512)``).

.. note::

    We don't use the ``fastmath`` option of Numba because the Numba backend
    does not support it yet!


Ahead-of-time compilation
-------------------------

.. literalinclude:: bench_aot.py

The results are:

.. code::

    transonic 0.4.0
    pythran 0.9.3post1
    numba 0.45.1

    laplace_transonic_pythran        : 1.00
    norm = 1.42e-04 s
    laplace_loops_transonic_pythran  : 0.95
    laplace_transonic_cython         : 8.36
    laplace_loops_transonic_cython   : 2.61
    laplace_numba                    : 8.94
    laplace_transonic_numba          : 8.93
    laplace_loops_numba              : 0.95
    laplace_loops_transonic_numba    : 0.95
    laplace_numpy                    : 7.01
    laplace_transonic_python         : 7.00