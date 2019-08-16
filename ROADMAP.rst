

Cython backend (beta version)
-----------------------------

Less bugs and more Cython features...

- Fused types rather than more than one signature
- "exterior" functions + understand the tests
- Recompile if pxd changed + "signature file" also for Pythran (``.pythran``)

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

Alternative syntax for blocks
-----------------------------

See `issue #6 <https://bitbucket.org/fluiddyn/transonic/issues/6>`_

Alternative implementations for specified backends
--------------------------------------------------

Which API?
