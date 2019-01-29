Other accelerators
==================

There are many projects which are able to accelerate Python-Numpy code. We'd
like to focus first on Numba, Cython and Cupy.

Transonic has to do different things for different accelerators:

- For Pythran (already supported):

.. code ::

  .py -(transonify)-> .py -(pythranize)-> .so

- For Cython:

.. code ::

  .py -(transonify)-> .pyc -(cythonize)-> .so

- For Numba and Cupy:

.. code ::

  .py -(transonify)-> .py

For all backends, there is a "transonify" step, but the produced Python code is
different and should be saved in different files.

For Cython, the backend file is not a Python file and therefore cannot be
imported.

For Numba, it can be efficient to have more loops than with pure-Numpy and
Pythran. So if Numba is not installed the Numba backend should use the original
function.

For some backends, there is no compilation, or the compilation is not handled
by Transonic (as for Numba).
