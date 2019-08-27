Backends (Pythran, Cython, Numba, ...)
======================================

Transonic can use different tools to accelerate the code. We use the name
"backend".

The default backend is Pythran and currently, one can choose other backends
with the environment variable :code:`TRANSONIC_BACKEND` (which has to be
"pythran", "cython", "numba" or "python").

.. toctree::
   :maxdepth: 2

   examples/row_sum/txt
   backends/pythran
   backends/cython
   backends/other
