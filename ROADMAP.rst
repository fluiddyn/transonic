Short term (milestone for 0.4.1)
--------------------------------

- Use Cython for Windows and Pythran for Linux/macOS
  (on this example https://github.com/martibosch/pylandstats/pull/2)
- alternative make_header_from_fdef_annotations for Cython
- More warnings if a file is not transpiled / compiled


Cython backend (beta version)
-----------------------------

Less bugs and more Cython features... Note that unfortunately we are `limited
by Cython bugs <backends/cython.html>`_!

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

- [done] Cython decorators (boundscheck, wraparound, cdivision, nonecheck)

- [done] void type

- [done] Correct use of fused types (only 1 set of annotations supported)

- Special function definitions

  * [done] inline
  * [done] return type
  * nogil

- better fused types

- nogil context manager

- casting

- locals annotations for

  * boost methods
  * blocks
  * jit functions
  * jit methods

- "exterior" functions + understand the tests


Better Numba backend
--------------------

- ``numba.jit`` (not only ``numba.njit``)
- ``fastmath`` argument


``transonic.dataclass`` decorator
---------------------------------

It would allow one to use ``numba.jitclass`` and Cython extension type.

A interesting goal would be to rewrite `pygbm
<https://github.com/ogrisel/pygbm>`_ (written in Numba) with Transonic. Note
that the Cython translation is `here
<https://github.com/scikit-learn/scikit-learn/tree/master/sklearn/ensemble/_hist_gradient_boosting>`_
in scikit-learn. Good Rosetta stone!


Backends as Transonic extensions
--------------------------------

We can try that with `pyccel <https://github.com/pyccel/pyccel>`_.


Alternative syntax for blocks
-----------------------------

See `issue #6 <https://bitbucket.org/fluiddyn/transonic/issues/6>`_


Alternative implementations for specified backends
--------------------------------------------------

Which API?


Parallelism
-----------

We can already use OpenMP with Transonic-Pythran. But OpenMP pragmas are not
understood by the other backends. Numba and Cython use different notations
(with ``prange``):

- https://cython.readthedocs.io/en/latest/src/userguide/parallelism.html
- https://numba.pydata.org/numba-doc/dev/user/parallel.html


PyCapsule & ``numba.cfunc``
---------------------------

- https://docs.python.org/3/c-api/capsule.html
- https://serge-sans-paille.github.io/pythran-stories/the-capsule-corporation.html
- https://numba.pydata.org/numba-doc/dev/user/cfunc.html
