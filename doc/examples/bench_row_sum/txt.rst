Unified code for different backends
===================================

We demonstrate here how Transonic can be used to accelerate a unique code with
different Python accelerators (so-called "backends", now, Pythran, Cython and
Numba).

The code of the functions is taken from this `Stackoverflow question
<https://stackoverflow.com/questions/57199248/memory-efficient-operations-between-arbitrary-columns-of-numpy-array>`_.

As usual with Transonic, two modes are available: ahead-of-time compilation
(with the :code:`boost` decorator) and just-in-time compilation (with the
:code:`jit` decorator).

For both examples, we use some common code in a file ``util.py``

.. literalinclude:: util.py

Ahead-of-time compilation
-------------------------

.. literalinclude:: row_sum_boost.py

To compile this file with different backends, one can run:

.. code:: bash

    transonic -b python row_sum_boost.py
    transonic -b cython row_sum_boost.py
    transonic -b numba row_sum_boost.py
    transonic -b pythran row_sum_boost.py -af "-march=native -DUSE_XSIMD"

To choose the backend, we can call for example:

.. code:: bash

    TRANSONIC_BACKEND="cython" python row_sum_boost.py

Then, on my PC ("gre"), I get::

    Python
    high level: 1.31e-03 s  (=  1.00 * norm)
    low level:  1.04e-01 s  (= 79.27 * norm)

    Cython
    high level: 1.29e-03 s  (=  0.99 * norm)
    low level:  4.10e-04 s  (=  0.31 * norm)

    Numba
    high level: 1.04e-03 s  (=  0.80 * norm)
    low level:  2.69e-04 s  (=  0.21 * norm)

    Pythran
    high level: 7.68e-04 s  (=  0.59 * norm)
    low level:  2.55e-04 s  (=  0.19 * norm)

The fastest solutions are in this case the Numba and Pythran backends for the
implementation with explicit loops.

As usual, Pythran gives quite good results with the high-level implementation,
but in this case, it is still more than twice slower than the implementation
with loops.

Cython does not accelerate high-level Numpy code but gives good results for the
implementation with loops.

Just-in-time compilation
------------------------

For JIT, type annotations for the arguments are not needed and it does not
really make sense to add type annotations for all local variables. We thus
remove all type annotations (which is bad for Cython).

.. literalinclude:: row_sum_jit.py

which gives::

    Python
    high level: 1.20e-03 s  (=  1.00 * norm)
    low level:  1.15e-01 s  (= 95.26 * norm)

    Cython
    high level: 1.25e-03 s  (=  1.04 * norm)
    low level:  1.22e-02 s  (= 10.18 * norm)

    Numba
    high level: 1.12e-03 s  (=  0.93 * norm)
    low level:  2.51e-04 s  (=  0.21 * norm)

    Pythran
    high level: 6.71e-04 s  (=  0.56 * norm)
    low level:  2.41e-04 s  (=  0.20 * norm)
