Benchmark expression broadcast
==============================

.. literalinclude:: bench.py

which gives::

    transonic 0.4.1
    pythran 0.9.3post1
    numba 0.46.0

    broadcast                        : 1.000
    norm = 1.53e-04 s
    broadcast_numba                  : 0.469
    broadcast_loops_numba            : 0.439
    broadcast_pythran                : 0.280
    broadcast_loops_pythran          : 0.416

For the solution with loops, the 2 backends are equally good.

For Pythran, it is even faster with the high level implementation!
