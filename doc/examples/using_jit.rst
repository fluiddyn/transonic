Cached Just-In-Time compilation
===============================

With Transonic, one can use the Ahead-Of-Time compiler Pythran in a
Just-In-Time mode. It is really the **easiest way to speedup a function with
Pythran**, just by adding a decorator! And it works also in notebooks!

.. literalinclude:: using_jit.py

Note that it can be very convenient to use type hints **and**
:code:`@jit` in order to avoid multiple warmup periods:

.. literalinclude:: using_jit_diff_types.py

If the environment variable :code:`TRANSONIC_COMPILE_AT_IMPORT` is set,
transonic compiles at import time the functions with type hints.
