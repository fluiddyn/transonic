Short term (Milestones for 0.4.0)
---------------------------------

- alternative make_header_from_fdef_annotations for Cython


setup.py & more than one backend at runtime
-------------------------------------------

Good example: https://github.com/martibosch/pylandstats/pull/1

- [done?] ``make_backend_files(backend_default="cython")``
- [done?] More than one backend at runtime
- [done] "python" backend (equivalent to NO_REPLACE)
- Warnings if file not compiled
- [done?] ``TRANSONIC_BACKEND`` changes only ``backend_default``
- Examples setup.py in documentation


[done?] Specify backend in code
-------------------------------

.. code:: python

  def func():
        return 1

  func_pythran = @jit(backend="pythran")(func)
  func_cython = @jit(backend="cython")(func)
  func_numba = @jit(backend="numba")(func)

And same with ``boost``.

- [done] Rewrite the comparison Numba / Pythran with Transonic

Cython backend (beta version)
-----------------------------

Less bugs and more Cython features...

- [done] Header also for Pythran (``.pythran``)
- [done] Refactore backends "for method"
- [done] Recompile if header changed
- [done] test_run.py: also check signature files
- [done] Fused types rather than more than one signature for

  * [done] boost functions
  * [done] boost methods
  * [done] blocks
  * [done] jit functions
  * [done] jit methods

- [done] BackendJITCython

- [done] Check/fix

  * [done] boost methods
  * [done] blocks
  * [done] jit functions
  * [done] jit methods

- Special function definitions

  * [done] inline
  * [done] return type
  * nogil

- [done] Cython decorators (:code:`@cython.boundscheck(False)
  @cython.wraparound(False)`)

- Correct use of fused types (only 1 set of annotations supported)

- locals annotations for

  * boost methods
  * blocks
  * jit functions
  * jit methods

- "exterior" functions + understand the tests

- void type

- nogil for function definition

- nogil context manager

``transonic.dataclass`` decorator
---------------------------------

It would allow one to use ``numba.jitclass`` and Cython extension type.

Alternative syntax for blocks
-----------------------------

See `issue #6 <https://bitbucket.org/fluiddyn/transonic/issues/6>`_

Alternative implementations for specified backends
--------------------------------------------------

Which API?
