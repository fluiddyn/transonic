Benchmark projection vector
===========================

.. literalinclude:: bench.py

This example uses the ``boost`` decorator, so the Python file needs to be
transpiled by Transonic and the accelerator files need to be compiled. You can
for example run from the directory ``doc/examples/bench_proj_perp``::

    make clean
    make
    python bench.py

The last command gives something like::

    Transonic 0.4.1
    Pythran 0.9.3post1
    Numba 0.46.0
    Cython 0.29.13

    proj                             : 1.00 * norm
    norm = 5.76e-01 s
    proj_cython                      : 1.26 * norm
    proj_loop_cython                 : 0.18 * norm
    proj_numba                       : 1.34 * norm
    proj_loop_numba                  : 0.15 * norm
    proj_pythran                     : 0.42 * norm
    proj_loop_pythran                : 0.14 * norm


For the solution with loops, the 3 backends are equally good.

Pythran also accelerates the high level implementation, but in this case, it is
still more than twice slower than the implementation with loops.
