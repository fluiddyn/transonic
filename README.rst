Transonic: Make your code fly at transonic speeds!
==================================================

|release| |docs| |coverage| |travis|

.. |release| image:: https://img.shields.io/pypi/v/transonic.svg
   :target: https://pypi.python.org/pypi/transonic/
   :alt: Latest version

.. |docs| image:: https://readthedocs.org/projects/transonic/badge/?version=latest
   :target: http://transonic.readthedocs.org
   :alt: Documentation status

.. |coverage| image:: https://codecov.io/bb/fluiddyn/transonic/branch/default/graph/badge.svg
   :target: https://codecov.io/bb/fluiddyn/transonic/branch/default/
   :alt: Code coverage

.. |travis| image:: https://travis-ci.org/fluiddyn/transonic.svg?branch=master
   :target: https://travis-ci.org/fluiddyn/transonic
   :alt: Travis CI status

Transonic is a fork of `FluidPythran
<https://bitbucket.org/fluiddyn/fluidpythran>`_ by its authors. It should
replace FluidPythran.

**Documentation**: https://transonic.readthedocs.io

.. warning ::

   Transonic is still in a quite early stage. Remarks and suggestions are
   very welcome.

   However, Transonic is now really usable and used "in production" in
   `FluidSim <https://bitbucket.org/fluiddyn/fluidsim>`_ and `FluidFFT
   <https://bitbucket.org/fluiddyn/fluidfft>`_ (see examples for `blocks
   <https://bitbucket.org/fluiddyn/fluidsim/src/default/fluidsim/base/time_stepping/pseudo_spect.py>`_,
   `@boost
   <https://bitbucket.org/fluiddyn/fluidfft/src/default/fluidfft/fft3d/operators.py>`_
   and `@cachedjit
   <https://bitbucket.org/fluiddyn/fluidsim/src/default/fluidsim/solvers/plate2d/output/correlations_freq.py>`_).

Transonic is a pure Python package (requiring Python >= 3.6 or Pypy3) to
help to write Python code that *can* use `Pythran
<https://github.com/serge-sans-paille/pythran>`_ if it is available.

Let's recall that "Pythran is an ahead-of-time (AOT) compiler for a subset of
the Python language, with a focus on scientific computing. It takes a Python
module annotated with a few interface description and turns it into a native
Python module with the same interface, but (hopefully) faster."

Pythran is able to produce **very efficient C++ code and binaries from high
level Numpy code**. If the algorithm is easier to express without loops, don't
write loops!

Pythran always releases the `GIL
<https://wiki.python.org/moin/GlobalInterpreterLock>`_ and can use `SIMD
instructions <https://github.com/QuantStack/xsimd>`_ and `OpenMP
<https://www.openmp.org/>`_!

**Pythran is not a hard dependency of Transonic:** Python code using
Transonic run fine without Pythran and without compilation (and of course
without speedup)!


Overview
--------

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

To summarize, a **strategy to quickly develop a very efficient scientific
application/library** with Python could be:

- Use modern Python coding, standard Numpy/Scipy for the computations and all
  the cool libraries you want.

- Profile your applications on real cases, detect the bottlenecks and apply
  standard optimizations with Numpy.

- Add few lines of Transonic to compile the hot spots.

**Implementation details:** Under the hood, Transonic creates Pythran files
(one per module for AOT compilation and one per function for JIT compilation)
that can be compiled at build, import or run times depending of the cases. Note
that the developers can still read the Pythran files if needed.

.. tip ::

  Transonic is really convenient for experimenting and benchmarking with
  Pythran (as for example these comparisons `with Julia
  <https://github.com/fluiddyn/BenchmarksPythonJuliaAndCo/tree/master/JuMicroBenchmarks>`_
  and `with Numba
  <https://transonic.readthedocs.io/en/latest/examples/using_cachedjit.html#comparison-numba-vs-transonic>`__):

  - The whole code can be gathered in one Python file.

  - With the :code:`@cachedjit` decorator, we don't need to add the types and
    to launch compilation commands!

  - Even without :code:`@cachedjit` (i.e. with AOT compilation), it is easy to
    trigger a mode in which Transonic automatically takes care of all
    compilation steps (see `set_compile_at_import <compile-at-import_>`__).

.. note ::

  Transonic can be used in libraries and applications using MPI (as
  `FluidSim <https://bitbucket.org/fluiddyn/fluidsim>`_).


Installation and configuration
------------------------------

.. code ::

   pip install transonic

.. _compile-at-import :

Transonic is sensible to environment variables:

- :code:`TRANSONIC_DIR` can be set to control where the cached files are
  saved.

- :code:`COMPILE_AT_IMPORT` can be set to enable a mode for which
  Transonic compiles at import time the Pythran file associated with the
  imported module. This behavior can also be triggered programmatically by using
  the function :code:`set_compile_at_import`.

- :code:`TRANSONIC_NO_REPLACE` can be set to disable all code replacements.
  This is useful to compare execution times and when measuring code coverage.

- :code:`FLUID_COMPILE_CACHEDJIT` can be set to false to disable the
  compilation of cachedjited functions. This can be useful for unittests.


A short tour of Transonic syntaxes
-------------------------------------

Decorator :code:`boost` and command :code:`# pythran def`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code :: python

    import h5py
    import mpi4py

    from transonic import boost

    # pythran def myfunc(int, float)

    @boost
    def myfunc(a, b):
        return a * b

    ...

Most of this code looks familiar to Pythran users. The differences:

- One can use (for example) h5py and mpi4py (of course not in the Pythran
  functions).

- :code:`# pythran def` instead of :code:`# pythran export` (to stress that it
  is not the same command).

- A tiny bit of Python... The decorator :code:`@boost` replaces the
  Python function by the pythranized function if Transonic has been used to
  produced the associated Pythran file.


Pythran using type annotations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The previous example can be rewritten without Pythran commands:

.. code :: python

    import h5py
    import mpi4py

    from transonic import boost

    @boost
    def myfunc(a: int, b: float):
        return a * b

    ...

Nice (shorter and clearer than with the Pythran command) but very limited... So
one can also elegantly define many Pythran signatures using in the annotations
type variables and Pythran types in strings (see `these examples
<https://transonic.readthedocs.io/en/latest/examples/type_hints.html>`_).
Moreover, it is possible to mix type hints and :code:`# pythran def` commands.

Cached Just-In-Time compilation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With Transonic, one can use the Ahead-Of-Time compiler Pythran in a
Just-In-Time mode. It is really the **easiest way to speedup a function with
Pythran**, just by adding a decorator! And it also works `in notebooks
<https://transonic.readthedocs.io/en/latest/ipynb/executed/demo_cachedjit.html>`_!

It is a "work in progress" so (i) it could be buggy and (ii) the API is not
great, but it is a good start!

.. code :: python

    import numpy as np

    # pythran import numpy as numpy

    from transonic import cachedjit, used_by_cachedjit

    @used_by_cachedjit("func1")
    def func0(a, b):
        return a + b

    @cachedjit
    def func1(a, b):
        return np.exp(a) * b * func0(a, b)

Note that the :code:`@cachedjit` decorator takes into account type hints (see
`the example in the documentation
<https://transonic.readthedocs.io/en/latest/examples/using_cachedjit.html>`_).

**Implementation details for just-in-time compilation:** A Pythran file is
produced for each "cachedjited" function (function decorated with
:code:`@cachedjit`). The file is compiled at the first call of the function and
the compiled version is used as soon as it is ready. The warmup can be quite
long but the compiled version is saved and can be reused (without warmup!) by
another process.


Command :code:`# pythran block`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Transonic blocks can be used with classes and more generally in functions
with lines that cannot be compiled by Pythran.

.. code :: python

    from transonic import Transonic

    fp = Transonic()

    class MyClass:

        ...

        def func(self, n):
            a, b = self.something_that_cannot_be_pythranized()

            if fp.is_transpiled:
                result = fp.use_block("name_block")
            else:
                # pythran block (
                #     float a, b;
                #     int n
                # ) -> result

                # pythran block (
                #     complex a, b;
                #     int n
                # ) -> result

                result = a**n + b**n

            return self.another_func_that_cannot_be_pythranized(result)

For blocks, we need a little bit more of Python.

- At import time, we have :code:`fp = Transonic()`, which detects which
  Pythran module should be used and imports it. This is done at import time
  since we want to be very fast at run time.

- In the function, we define a block with three lines of Python and special
  Pythran annotations (:code:`# pythran block`). The 3 lines of Python are used
  (i) at run time to choose between the two branches (:code:`is_transpiled` or
  not) and (ii) at compile time to detect the blocks.

Note that the annotations in the command :code:`# pythran block` are different
(and somehow easier to write) than in the standard command :code:`# pythran
export`.

`Blocks can now also be defined with type hints!
<https://transonic.readthedocs.io/en/latest/examples/blocks.html>`_

.. warning ::

   I'm not satisfied by the syntax for Pythran blocks so I (PA) proposed an
   alternative syntax in `issue #29
   <https://bitbucket.org/fluiddyn/fluidpythran/issues/29>`_.

Python classes: :code:`@boost` and :code:`@cachedjit` for methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For simple methods **only using attributes**, we can write:

.. code :: python

    import numpy as np

    from transonic import boost

    A = "float[:]"

    @boost
    class MyClass:

        arr0: A
        arr1: A

        def __init__(self, n):
            self.arr0 = np.zeros(n)
            self.arr1 = np.zeros(n)

        @boost
        def compute(self, alpha: float):
            return (self.arr0 + self.arr1).mean() ** alpha

.. warning ::

   Calling another method in a Pythranized method is not yet supported!

More examples of how to use Transonic for Object Oriented Programing are
given `here
<https://transonic.readthedocs.io/en/latest/examples/methods.html>`__.


Make the Pythran files
----------------------

There is a command-line tool :code:`transonic` which makes the associated
Pythran files from Python files with annotations and transonic code. By
default and if Pythran is available, the Pythran files are compiled.

There is also a function :code:`make_pythran_files` that can be used in a
setup.py like this:

.. code ::

    from pathlib import Path

    from transonic.dist import make_pythran_files

    here = Path(__file__).parent.absolute()

    paths = ["fluidsim/base/time_stepping/pseudo_spect.py"]
    make_pythran_files([here / path for path in paths], mocked_modules=["h5py"])

Note that the function :code:`make_pythran_files` does not use Pythran.
Compiling the associated Pythran file can be done if wanted (see for example
how it is done in the example package `example_package_fluidpythran
<https://bitbucket.org/fluiddyn/example_package_fluidpythran>`_ or in
`fluidsim's setup.py
<https://bitbucket.org/fluiddyn/fluidsim/src/default/setup.py>`_).

License
-------

FluidDyn is distributed under the CeCILL-B_ License, a BSD compatible
french license.

.. _CeCILL-B: http://www.cecill.info/index.en.html
