Other accelerators
==================

There are many projects which are able to accelerate Python-Numpy code. We'd
like to focus first on Numba, Cython and Cupy.

Transonic has to do different things for different accelerators:

- For Pythran:

.. code ::

  .py -(transonify)-> .py -(pythranize)-> .so

- For Cython:

.. code ::

  .py -(transonify)-> (.py + .pxd) -(cythonize)-> .so

- For Numba and Cupy:

.. code ::

  .py -(transonify)-> .py
