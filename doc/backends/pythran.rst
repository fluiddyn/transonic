Pythran backend
===============

Why Pythran is great for Python users doing numerical computing?
----------------------------------------------------------------

Let's recall that "Pythran is an ahead-of-time (AOT) compiler for a subset of
the Python language, with a focus on scientific computing. It takes a Python
module annotated with a few interface description and turns it into a native
Python module with the same interface, but (hopefully) faster."

Pythran is able to produce **very efficient C++ code and binaries from high
level Numpy code**. Broadcasting (for example :code:`2*a**2 + 6*b*c`, where
:code:`a`, :code:`b` and :code:`c` are Numpy arrays) is **very fast** with
Pythran. If the algorithm is easier to express without loops, don't write
loops!

Pythran always releases the `GIL
<https://wiki.python.org/moin/GlobalInterpreterLock>`_ and can use `SIMD
instructions <https://github.com/QuantStack/xsimd>`_ and `OpenMP
<https://www.openmp.org/>`_!

Why Transonic is great for Pythran users?
-----------------------------------------

Python + Numpy + Pythran is a great combo to easily write highly efficient
scientific programs and libraries.

To use Pythran, one needs to isolate the numerical kernels functions in modules
that are compiled by Pythran. The C++ code produced by Pythran never uses the
Python interpreter. It means that only a subset of what is doable in Python can
be done in Pythran files. Some `language features
<https://pythran.readthedocs.io/en/latest/MANUAL.html#disclaimer>`_ are not
supported by Pythran (for example no classes) and most of the extension
packages cannot be used in Pythran files (basically `only Numpy and some Scipy
functions <https://pythran.readthedocs.io/en/latest/SUPPORT.html>`_).

Another cause of frustration for Python developers when using Pythran is
related to manual writting of Pythran function signatures in comments, which
can not be automated. Pythran uses C++ templates but Pythran users can not
think with this concept. We would like to be able to **express the templated
nature of Pythran with modern Python syntax** (in particular **type
annotations**).

Finally, another limitation is that it is not possible to use Pythran for
**just-in-time** (JIT) compilation so one needs to manually write all argument
types.

With Transonic, we try to overcome these limitations. Transonic provides
few supplementary Pythran commands and a small Python API to accelerate
functions and methods with Pythran without writing the Pythran modules. The
code of the numerical kernels can stay in the modules and in the classes where
they were written. The Pythran files (i.e. the files compiled by Pythran),
which are usually written by the user, are produced automatically by
Transonic.

Bonus: There are Transonic syntaxes for both **ahead-of-time** and
**just-in-time** compilations!

At run time, Transonic uses when possible the pythranized functions, but
let's stress again that codes using Transonic work fine without Pythran (of
course without speedup)!

**Implementation details:** Under the hood, Transonic creates Pythran files
(one per module for AOT compilation and one per function for JIT compilation)
that can be compiled at build, import or run times depending of the cases. Note
that the developers can still read the Pythran files if needed.

.. tip ::

  Transonic is really convenient for experimenting and benchmarking with
  Pythran (as for example these comparisons `with Julia
  <https://github.com/fluiddyn/BenchmarksPythonJuliaAndCo/tree/master/JuMicroBenchmarks>`_
  and `with Numba
  <https://transonic.readthedocs.io/en/latest/examples/using_jit.html#comparison-numba-vs-transonic>`__):

  - The whole code can be gathered in one Python file.

  - With the :code:`@jit` decorator, we don't need to add the types and
    to launch compilation commands!

  - Even without :code:`@jit` (i.e. with AOT compilation), it is easy to
    trigger a mode in which Transonic automatically takes care of all
    compilation steps (see :ref:`compile-at-import`).
