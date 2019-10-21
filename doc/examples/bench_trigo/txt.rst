Benchmark rotation vector
=========================

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

    fxfy                             : 1.000 * norm
    norm = 6.76e-04 s
    fxfy_numba                       : 0.969 * norm
    fxfy_loops_numba                 : 0.792 * norm
    fxfy_pythran                     : 0.123 * norm
    fxfy_loops_pythran               : 0.787 * norm

For the solution with loops, the 2 backends are equally good.

For Pythran, it is much faster with the high level implementation!
