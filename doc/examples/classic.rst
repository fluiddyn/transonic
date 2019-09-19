Nearly as with Pythran
======================

This example shows how to use Transonic nearly `how you would use Pythran
<https://pythran.readthedocs.io>`_.

.. literalinclude:: classic.py

Most of this code looks familiar to Pythran users. The differences:

- One can use (for example) h5py and mpi4py (of course not in the Pythran
  functions).

- :code:`# transonic def` instead of :code:`# pythran export`.

- A tiny bit of Python... The decorator :code:`@boost` replaces the
  Python function by the pythranized function if Transonic has been used to
  produced the associated Pythran file.

Function calls
~~~~~~~~~~~~~~

Boosted functions support function calls, including imported functions from
a Python file in the same directory!

.. literalinclude:: classic_func_using_func.py

Note that no Pythran signatures or annotations are needed for functions called
in boosted functions.
