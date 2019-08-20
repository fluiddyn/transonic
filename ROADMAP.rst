Cython backend (beta version)
-----------------------------

Less bugs and more Cython features...

- Header also for Pythran (``.pythran``)
- Recompile if pxd changed
- Refactore backends "for method"
- BackendJITCython
- Fused types rather than more than one signature
- "exterior" functions + understand the tests
- test_run.py: also check signature files
- Check/fix

  * jit functions
  * boost methods
  * jit methods
  * blocks

setup.py & more than one backend at runtime
-------------------------------------------

- ``make_backend_files(backend_default="cython")``
- More than one backend at runtime
- "python" backend (equivalent to NO_REPLACE)
- Warnings if file not compiled
- ``TRANSONIC_BACKEND`` changes only ``backend_default``
- Examples setup.py in documentation

Numba backend
-------------

Simpler but not so simple because no compilation!

We could solve this by having 2 files. A "backend file" (mod.py):

.. code:: python

  #__protected__ import numba as nb

  #__protected__ @nb.jit
  def func(...):
      ...


and a "compiled file" (mod_[hash].py):

.. code:: python

  import numba as nb

  @nb.jit
  def func(...):
      ...

Specify backend in code
-----------------------

.. code:: python

  def func():
        return 1

  func_pythran = @jit(backend="pythran")(func)
  func_cython = @jit(backend="cython")(func)
  func_numba = @jit(backend="numba")(func)

And same with ``boost``.

- Rewrite the comparison Numba / Pythran with Transonic

- A page on [this
  case](https://stackoverflow.com/questions/57199248/memory-efficient-operations-between-arbitrary-columns-of-numpy-array)
  in the documentation

Alternative syntax for blocks
-----------------------------

See `issue #6 <https://bitbucket.org/fluiddyn/transonic/issues/6>`_

Alternative implementations for specified backends
--------------------------------------------------

Which API?
