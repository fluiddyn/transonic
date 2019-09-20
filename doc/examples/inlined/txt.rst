:code:`inline` functions
========================

.. literalinclude:: add.py

Compiled with:

.. code:: bash

    transonic -b pythran add.py
    transonic -b numba add.py
    transonic -b cython add.py

Gives:

.. code:: bash

    TRANSONIC_NO_REPLACE=1 python add.py
     8.43e-03 s
    TRANSONIC_BACKEND="pythran" python add.py
     1.34e-07 s
    TRANSONIC_BACKEND="numba" python add.py
     1.53e-07 s
    TRANSONIC_BACKEND="cython" python add.py
     3.24e-07 s

The three backends and their compilers give very good speedup!
