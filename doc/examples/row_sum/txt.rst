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
    transonic -b pythran row_sum_boost.py -pf "-march=native -DUSE_XSIMD"

Then, on my PC (meige8pcpa79), I get::

    TRANSONIC_BACKEND="python" python row_sum_boost.py
    Checks passed: results are consistent
    Python
    row_sum              2.0e-03 s
    row_sum_loops        1.6e-01 s

    TRANSONIC_BACKEND="cython" python row_sum_boost.py
    Checks passed: results are consistent
    Cython
    row_sum              2.0e-03 s
    row_sum_loops        5.2e-04 s

    TRANSONIC_BACKEND="numba" python row_sum_boost.py
    Checks passed: results are consistent
    Numba
    row_sum              1.9e-03 s
    row_sum_loops        4.4e-04 s

    TRANSONIC_BACKEND="pythran" python row_sum_boost.py
    Checks passed: results are consistent
    Pythran
    row_sum              1.1e-03 s
    row_sum_loops        4.2e-04 s

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

    TRANSONIC_BACKEND="cython" python row_sum_jit.py
    Checks passed: results are consistent
    Checks passed: results are consistent
    Cython
    row_sum              1.3e-03 s
    row_sum_loops        1.2e-02 s

    TRANSONIC_BACKEND="numba" python row_sum_jit.py
    Checks passed: results are consistent
    Checks passed: results are consistent
    Numba
    row_sum              1.1e-03 s
    row_sum_loops        2.7e-04 s

    TRANSONIC_BACKEND="pythran" python row_sum_jit.py
    Checks passed: results are consistent
    Checks passed: results are consistent
    Pythran
    row_sum              8.4e-04 s
    row_sum_loops        2.6e-04 s
