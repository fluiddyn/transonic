Benchmark projection vector
===========================

.. literalinclude:: proj.py

which gives::

    transonic 0.4.1
    pythran 0.9.3post1
    numba 0.46.0

    proj                             : 1.00
    norm = 4.46e-01 s
    proj_cython                      : 1.26
    proj_loop_cython                 : 0.23
    proj_numba                       : 1.09
    proj_loop_numba                  : 0.22
    proj_pythran                     : 0.46
    proj_loop_pythran                : 0.22


For the solution with loops, the 3 backends are equally good.

Pythran also accelerates the high level implementation, but in this case, it is
still more than twice slower than the implementation with loops.
