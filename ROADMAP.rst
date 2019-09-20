Short term (Milestone for 0.4.1)
--------------------------------

- Use Cython for Windows and Pythran for Linux/macOS
  (on this example https://github.com/martibosch/pylandstats/pull/1)
- alternative make_header_from_fdef_annotations for Cython
- More warnings if file not compiled


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
