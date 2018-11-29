Nearly as with Pythran
======================

This example shows how to use FluidPythran nearly `how you would use Pythran
<https://pythran.readthedocs.io>`_.

.. literalinclude:: classic.py

Most of this code looks familiar to Pythran users. The differences:

- One can use (for example) h5py and mpi4py (of course not in the Pythran
  functions).

- :code:`# pythran def` instead of :code:`# pythran export` (to stress that it
  is not the same command).

- A tiny bit of Python... The decorator :code:`@pythran_def` replaces the
  Python function by the pythranized function if FluidPythran has been used to
  produced the associated Pythran file.

In this very simple mode, fluidpythran does not need to import the module to
produce the Pythran files. If we do not want fluidpythran to import the module,
we can use the command :code:`# FLUIDPYTHRAN_NO_IMPORT`.
