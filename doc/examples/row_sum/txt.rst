Unified code for different backends
===================================

We demonstrate here how Transonic can be used to accelerate an unique code with
different backends (Pythran, Cython and Numba).

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

    TRANSONIC_BACKEND="cython" transonic row_sum_boost.py
    TRANSONIC_BACKEND="numba" transonic row_sum_boost.py
    TRANSONIC_BACKEND="pythran" transonic row_sum_boost.py -pf "-march=native -DUSE_XSIMD"
    TRANSONIC_BACKEND="python" transonic row_sum_boost.py

Then, on my PC, I get::

    TRANSONIC_BACKEND="python" python row_sum_boost.py
    Checks passed: results are consistent
    Python
    row_sum_loops        108.57 s
    row_sum_transpose    1.38

    TRANSONIC_BACKEND="cython" python row_sum_boost.py
    Checks passed: results are consistent
    Cython
    row_sum_loops        0.45 s
    row_sum_transpose    1.32 s

    TRANSONIC_BACKEND="numba" python row_sum_boost.py
    Checks passed: results are consistent
    Numba
    row_sum_loops        0.27 s
    row_sum_transpose    1.16 s

    TRANSONIC_BACKEND="pythran" python row_sum_boost.py
    Checks passed: results are consistent
    Pythran
    row_sum_loops        0.27 s
    row_sum_transpose    0.76 s

The fastest solutions are in this case the implementation with loops and the
Numba and Pythran backends.

As usual, Pythran gives quite good results with the high-level implementation,
but in this case, it is still more than twice slower than the implementation
with loops.

Just-in-time compilation
------------------------

For JIT, type annotations for the arguments are not needed and it does not
really make sense to add type annotations for local variables.

.. literalinclude:: row_sum_jit.py

which gives::

    TRANSONIC_BACKEND="cython" python row_sum_jit.py
    Checks passed: results are consistent
    Checks passed: results are consistent
    Cython
    row_sum_loops        11.94 s
    row_sum_transpose    1.28 s

    TRANSONIC_BACKEND="numba" python row_sum_jit.py
    Checks passed: results are consistent
    Checks passed: results are consistent
    Numba
    row_sum_loops        0.28 s
    row_sum_transpose    1.14 s

    TRANSONIC_BACKEND="pythran" python row_sum_jit.py
    Checks passed: results are consistent
    Checks passed: results are consistent
    Pythran
    row_sum_loops        0.28 s
    row_sum_transpose    0.76 s
