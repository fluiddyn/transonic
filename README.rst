Make your Python code fly at *transonic* speeds!
================================================

|release| |docs| |coverage| |travis| |appveyor|

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

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/i99h00kp0jliel8t?svg=true
   :target: https://ci.appveyor.com/project/fluiddyn/transonic
   :alt: AppVeyor status

**Documentation**: https://transonic.readthedocs.io

Transonic is a pure Python package (requiring Python >= 3.6) to easily
accelerate modern Python-Numpy code with different accelerators (like Cython,
`Pythran <https://github.com/serge-sans-paille/pythran>`_, Numba, Cupy,
PyTorch, Uarray, etc...) opportunistically (i.e. if/when they are available).

**The accelerators are not hard dependencies of Transonic:** Python codes using
Transonic run fine without any accelerators installed (of course without
speedup)!

.. warning ::

  Transonic is still in a early stage. Remarks and suggestions are very
  welcome.

  In particular, Transonic is now only able to use the Pythran compiler! So you
  are not going to be able to use for example Numba with this version of
  Transonic.

  However, Transonic is now really usable, useful and used "in production" in
  `FluidSim <https://bitbucket.org/fluiddyn/fluidsim>`_ and `FluidFFT
  <https://bitbucket.org/fluiddyn/fluidfft>`_ (see examples for `blocks
  <https://bitbucket.org/fluiddyn/fluidsim/src/default/fluidsim/base/time_stepping/pseudo_spect.py>`_,
  `@boost
  <https://bitbucket.org/fluiddyn/fluidfft/src/default/fluidfft/fft3d/operators.py>`_
  and `@jit
  <https://bitbucket.org/fluiddyn/fluidsim/src/default/fluidsim/solvers/plate2d/output/correlations_freq.py>`_).


The long-term project
---------------------

.. note ::

  The context of the creation of Transonic is presented in these slices:
  `Overview of the Python HPC landscape and zoom on Transonic
  <http://www.legi.grenoble-inp.fr/people/Pierre.Augier/docs/ipynbslides/20190319_PySciDataGre_transonic/pres_20190319_PySciDataGre_transonic.slides.html>`_.

Transonic targets Python end-users and library developers.

It is based on the following principles:

- We'd like to write scientific / computing applications / libraries with
  pythonic, readable, modern code (Python >= 3.6).

- In some cases, Python-Numpy is too slow. However, there are tools to
  accelerate such Python-Numpy code which lead to very good performances!

- Let's try to write universal code which express what we want to compute and
  not the special hacks we want to use to make it fast. We just need nice ways
  to express that a function, a method or a block of code has to be accelerated
  (and how it has to be accelerated). We'd like to be able to do this in a
  pythonic way, with decorators and context managers.

- There are many tools to accelerate Python-Numpy code! Let's avoid writting
  code specialized for only one of these tools.

- Let's try to keep the code as it would be written without acceleration. For
  example, with Transonic, we are able to accelerate (simple) methods of classes
  even though some accelerators don't support classes.

- Let's accelerate/compile only what needs to be accelerated, i.e. only the
  bottlenecks. Python and its interpreters are good for the rest. In most
  cases, the benefice of writting big compiled extensions (with Cython or in
  other languages) is negligible.

- Adding types is sometimes necessary. In modern Python, we have nice syntaxes
  for type annotations! Let's use them.

- Ahead-of-time (AOT) and just-in-time (JIT) compilation modes are both useful.
  We'd like to have a nice, simple and unified API for these two modes.

  * AOT is useful to be able to distribute compiled packages and in some cases,
    more optimizations can be applied.

  * JIT is simpler to use (no need for type annotations) and optimizations can
    be more hardware specific.

  Note that with Transonic, AOT compilers can be used as JIT compilers (with a
  cache mechanism).

  In contrast, some JIT compilers cannot be used as AOT compilers. For these
  tools, the AOT decorators will be used in a JIT mode.

To summarize, a **strategy to quickly develop a very efficient scientific
application/library** with Python could be:

1. Use modern Python coding, standard Numpy/Scipy for the computations and all
   the cool libraries you want.

2. Profile your applications on real cases, detect the bottlenecks and apply
   standard optimizations with Numpy.

3. Add few lines of Transonic to compile the hot spots.

What we have now
----------------

We start to have a good API to accelerate Python-Numpy code.

The only implemented Transonic backend uses Pythran and works well.

`Here, we explain why Pythran is so great for Python users and why Transonic is
great for Pythran users
<https://transonic.readthedocs.io/en/latest/pythran_backend.html>`_

.. note ::

  Transonic can be used in libraries and applications using MPI (as
  `FluidSim <https://bitbucket.org/fluiddyn/fluidsim>`_).

.. _compile-at-import :

Installation and configuration
------------------------------

.. code ::

   pip install transonic

Transonic is sensible to environment variables:

- :code:`TRANSONIC_DIR` can be set to control where the cached files are
  saved.

- :code:`TRANSONIC_DEBUG` triggers a verbose mode.

- :code:`TRANSONIC_COMPILE_AT_IMPORT` can be set to enable a mode for which
  Transonic compiles at import time the Pythran file associated with the
  imported module. This behavior can also be triggered programmatically
  by using the function :code:`set_compile_at_import`.

- :code:`TRANSONIC_NO_REPLACE` can be set to disable all code replacements.
  This is useful to compare execution times and when measuring code coverage.

- :code:`TRANSONIC_COMPILE_JIT` can be set to false to disable the
  compilation of jited functions. This can be useful for unittests.


A short tour of Transonic syntaxes
-------------------------------------

Decorator :code:`boost` and command :code:`# transonic def`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code :: python

    import h5py
    import mpi4py

    from transonic import boost

    # transonic def myfunc(int, float)

    @boost
    def myfunc(a, b):
        return a * b

    ...

Most of this code looks familiar to Pythran users. The differences:

- One can use (for example) h5py and mpi4py (of course not in the Pythran
  functions).

- :code:`# transonic def` instead of :code:`# pythran export`.

- A tiny bit of Python... The decorator :code:`@boost` replaces the
  Python function by the pythranized function if Transonic has been used to
  produced the associated Pythran file.


Pythran using type annotations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The previous example can be rewritten without :code:`# transonic def`. It is
the recommended syntaxes for ahead-of-time function acceleration:

.. code :: python

    import numpy as np
    import h5py

    from transonic import boost

    @boost
    def myfunc(a: float, d: int):
        return a * np.ones(d * [10])

    ...

Nice (shorter and clearer than with the Pythran command) but very limited... So
one can also elegantly define many Pythran signatures using in the annotations
type variables and Pythran types in strings (see `these examples
<https://transonic.readthedocs.io/en/latest/examples/type_hints.html>`_).
Moreover, it is possible to mix type hints and :code:`# transonic def` commands.

Just-In-Time compilation
~~~~~~~~~~~~~~~~~~~~~~~~

With Transonic, one can use the Ahead-Of-Time compiler Pythran in a
Just-In-Time mode. It is really the **easiest way to speedup a function with
Pythran**, just by adding a decorator! And it also works `in notebooks
<https://transonic.readthedocs.io/en/latest/ipynb/executed/demo_jit.html>`_!

.. code :: python

    import numpy as np

    from transonic import jit

    def func0(a, b):
        return a + b

    @jit
    def func1(a, b):
        return np.exp(a) * b * func0(a, b)

Note that the :code:`@jit` decorator takes into account type hints (see
`the example in the documentation
<https://transonic.readthedocs.io/en/latest/examples/using_jit.html>`_).

**Implementation details for just-in-time compilation:** A Pythran file is
produced for each "JITed" function (function decorated with :code:`@jit`). The
file is compiled at the first call of the function and the compiled version is
used as soon as it is ready. The warmup can be quite long but the compiled
version is saved and can be reused (without warmup!) by another process.


Define accelerated blocks
~~~~~~~~~~~~~~~~~~~~~~~~~

Transonic blocks can be used with classes and more generally in functions
with lines that cannot be compiled by Pythran.

.. code :: python

    from transonic import Transonic

    ts = Transonic()

    class MyClass:

        ...

        def func(self, n):
            a, b = self.something_that_cannot_be_pythranized()

            if ts.is_transpiled:
                result = ts.use_block("name_block")
            else:
                # transonic block (
                #     float a, b;
                #     int n
                # )

                # transonic block (
                #     complex a, b;
                #     int n
                # )

                result = a**n + b**n

            return self.another_func_that_cannot_be_pythranized(result)

For blocks, we need a little bit more of Python.

- At import time, we have :code:`ts = Transonic()`, which detects which
  Pythran module should be used and imports it. This is done at import time
  since we want to be very fast at run time.

- In the function, we define a block with three lines of Python and special
  Pythran annotations (:code:`# transonic block`). The 3 lines of Python are used
  (i) at run time to choose between the two branches (:code:`is_transpiled` or
  not) and (ii) at compile time to detect the blocks.

Note that the annotations in the command :code:`# transonic block` are different
(and somehow easier to write) than in the standard command :code:`# pythran
export`.

`Blocks can now also be defined with type hints!
<https://transonic.readthedocs.io/en/latest/examples/blocks.html>`_

.. warning ::

   I'm not satisfied by the syntax for Pythran blocks so I (PA) proposed an
   alternative syntax in `issue #29
   <https://bitbucket.org/fluiddyn/fluidpythran/issues/29>`_.

Python classes: :code:`@boost` and :code:`@jit` for methods
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

There is also a function :code:`make_backend_files` that can be used in a
setup.py like this:

.. code ::

    from pathlib import Path

    from transonic.dist import make_backend_files

    here = Path(__file__).parent.absolute()

    paths = ["fluidsim/base/time_stepping/pseudo_spect.py"]
    make_backend_files([here / path for path in paths])

Note that the function :code:`make_backend_files` does not use compile the file
produced. The compilation has to be done after the call of this function (see
for example how it is done in the example package `example_package_fluidpythran
<https://bitbucket.org/fluiddyn/example_package_fluidpythran>`_ or in
`fluidsim's setup.py
<https://bitbucket.org/fluiddyn/fluidsim/src/default/setup.py>`_).

License
-------

Transonic is distributed under the CeCILL-B_ License, a BSD compatible
french license.

.. _CeCILL-B: http://www.cecill.info/index.en.html
