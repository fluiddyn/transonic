Benchmark projection vector
===========================

.. literalinclude:: bench.py

which gives::

    transonic 0.4.1
    pythran 0.9.3post1
    numba 0.46.0

    proj                             : 1.00
    norm = 5.76e-01 s
    proj_cython                      : 1.26
    proj_loop_cython                 : 0.18
    proj_numba                       : 1.34
    proj_loop_numba                  : 0.15
    proj_pythran                     : 0.42
    proj_loop_pythran                : 0.14

For the solution with loops, the 3 backends are equally good.

Pythran also accelerates the high level implementation, but in this case, it is
still more than twice slower than the implementation with loops.
