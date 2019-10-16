Benchmark rotation vector
=========================

.. literalinclude:: bench.py

which gives::

    transonic 0.4.1
    pythran 0.9.3post1
    numba 0.46.0

    fxfy                             : 1.000
    norm = 6.69e-04 s
    fxfy_numba                       : 0.978
    fxfy_loops_numba                 : 0.797
    fxfy_pythran                     : 0.123
    fxfy_loops_pythran               : 0.800

For the solution with loops, the 2 backends are equally good.

For Pythran, it is much faster with the high level implementation!
