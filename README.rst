FluidPythran: use Pythran in non-pythranizable code
===================================================

|release| |docs| |coverage|

.. |release| image:: https://img.shields.io/pypi/v/fluidpythran.svg
   :target: https://pypi.python.org/pypi/fluidpythran/
   :alt: Latest version

.. |docs| image:: https://readthedocs.org/projects/fluidpythran/badge/?version=latest
   :target: http://fluidpythran.readthedocs.org
   :alt: Documentation status

.. |coverage| image:: https://codecov.io/bb/fluiddyn/fluidpythran/branch/default/graph/badge.svg
   :target: https://codecov.io/bb/fluiddyn/fluidpythran/branch/default/
   :alt: Code coverage


.. warning ::

   FluidPythran is still just a prototype. Remarks and suggestions are very
   welcome.

   FluidPythran just starts to be used in `FluidSim
   <https://bitbucket.org/fluiddyn/fluidsim>`_ (for example in `this file
   <https://bitbucket.org/fluiddyn/fluidsim/src/default/fluidsim/base/time_stepping/pseudo_spect.py>`_).

   See also `this blog post
   <http://www.legi.grenoble-inp.fr/people/Pierre.Augier/broadcasting-numpy-abstraction-cython-pythran-fluidpythran.html>`_
   for an explanation of my motivations.

FluidPythran is a pure Python package (requiring Python >= 3.6 or Pypy3) to
help to write Python code that can use `Pythran
<https://github.com/serge-sans-paille/pythran>`_.

Let's recall that "Pythran is an ahead of time compiler for a subset of the
Python language, with a focus on scientific computing. It takes a Python module
annotated with a few interface description and turns it into a native Python
module with the same interface, but (hopefully) faster."

**FluidPythran does not depend on Pythran.**

Overview
--------

Python + Numpy + Pythran is a great combo to easily write highly efficient
scientific programs and libraries.

To use Pythran, one needs to isolate the numerical kernels functions in modules
that are compiled by Pythran. The C++ code produced by Pythran never uses the
Python interpretor. It means that only a subset of what is doable in Python can
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

With FluidPythran, we try to overcome these limitations. FluidPythran provides
few supplementary Pythran commands and a small Python API to define Pythran
functions without writing the Pythran modules. The code of the numerical
kernels can stay in the modules and in the classes where they were written. The
Pythran files (i.e. the files compiled by Pythran), which are usually written
by the user, are produced automatically by FluidPythran.

There are FluidPythran syntaxes for both ahead-of-time and just-in-time
compilations.

At run time, FluidPythran uses when possible the pythranized functions.

Let's stress again that codes using FluidPythran work fine without Pythran!

**Implementation details for ahead-of-time compilation:** For each Python file
using FluidPythran, an associated Pythran file is created in a directory
:code:`_pythran`. For example, for a Python file :code:`foo.py`, the associated
file would be :code:`_pythran/_foo.py`.

**Implementation details for just-in-time compilation:** A Pythran file is
produced for each "cachedjited" function (function decorated with
:code:`@cachedjit`). The file is compiled at the first call of the function and
the compiled version is used as soon as it is ready. The warmup can be quite
long but the compiled version is saved and can be reused (without warmup!) by
another process.

Installation
------------

.. code ::

   pip install fluidpythran

Using Pythran in Python files
-----------------------------

Command :code:`# pythran def`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code :: python

    import h5py
    import mpi4py

    from fluidpythran import pythran_def

    # pythran def myfunc(int, float)

    @pythran_def
    def myfunc(a, b):
        return a * b

    ...

Most of this code looks familiar to Pythran users. The differences:

- One can use (for example) h5py and mpi4py (of course not in the Pythran
  functions).

- :code:`# pythran def` instead of :code:`# pythran export` (to stress that it
  is not the same command).

- A tiny bit of Python... The decorator :code:`@pythran_def` replaces the
  Python function by the pythranized function if FluidPythran has been used to
  produced the associated Pythran file.

Pythran using type annotations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The previous example can be rewritten without Pythran commands:

.. code :: python

    import h5py
    import mpi4py

    from fluidpythran import pythran_def

    @pythran_def
    def myfunc(a: int, b: float):
        return a * b

    ...

Nice but very limited... So it possible to mix type hints and :code:`# pythran
def` commands.

Moreover, if you like C++11 :code:`template`, you can write (see `issue #5
<https://bitbucket.org/fluiddyn/fluidpythran/issues/5>`_):

.. code :: python

    import numpy as np
    import fluidpythran as fp
    from fluidpythran import Type, NDim, Array

    T = Type("T")
    N = NDim("N")

    A = Array[T, N]
    A1 = Array[np.float32, N + 1]

    @fp.pythran_def
    def compute(a: A, b: A, c: T, d: A1, e: str):
        print(e)
        tmp = a + b
        return tmp

    for dtype in [int, np.complex128]:
        for ndim in [1, 3]:
            fp.make_signature(compute, T=dtype, N=ndim)


If you don't like generic templating, you can also just write

.. code :: python

    import numpy as np
    import fluidpythran as fp
    from fluidpythran import Type, NDim, Array

    T = Type(int, np.complex128)
    N = NDim(1, 3)

    A = Array[T, N]
    A1 = Array[np.float32, N + 1]

    @fp.pythran_def
    def compute(a: A, b: A, c: T, d: A1, e: str):
        print(e)
        tmp = a + b
        return tmp


Command :code:`# pythran block`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

One of the most evident application of :code:`# pythran block` is code in
classes:

.. code :: python

    from fluidpythran import FluidPythran

    fp = FluidPythran()

    class MyClass:

        ...

        def func(self, n):
            a, b = self.something_that_cannot_be_pythranized()

            if fp.is_pythranized:
                result = fp.use_pythranized_block("name_block")
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

- At import time, we have :code:`fp = FluidPythran()`, which detects which
  Pythran module should be used and imports it. This is done at import time
  since we want to be very fast at run time.

- In the function, we define a block with three lines of Python and special
  Pythran annotations (:code:`# pythran block`). The 3 lines of Python are used
  (i) at run time to choose between the two branches (:code:`is_pythranized` or
  not) and (ii) at compile time to detect the blocks.

Note that the annotations in the command :code:`# pythran block` are different
(and somehow easier to write) than in the standard command :code:`# pythran
export`.

.. note ::

    Moreover, for the time being, one needs to explicitly write the "returned"
    variables (after :code:`->`). However, it is a redundant information so we
    could avoid this in future (see `issue #1
    <https://bitbucket.org/fluiddyn/fluidpythran/issues/1/no-need-for-explicit-return-values-in>`_).

.. warning ::

    The two branches of the :code:`if fp.is_pythranized` are not equivalent! The
    user has to be careful because it is not difficult to write such buggy code:

    .. code :: python

        c = 0
        if fp.is_pythranized:
            a, b = fp.use_pythranized_block("buggy_block")
        else:
            # pythran block () -> (a, b)
            a = b = c = 1

        assert c == 1

.. note ::

    The Pythran keyword :code:`or` cannot be used in block annotations (not yet
    implemented, see `issue #2
    <https://bitbucket.org/fluiddyn/fluidpythran/issues/2/implement-keyword-or-in-block-annotation>`_).

Blocks can now be defined with type hints!

.. code :: python

    from fluidpythran import FluidPythran, Type, NDim, Array

    fp = FluidPythran()

    T = Type(float, complex)
    N = NDim(1, 2, 3)
    A = Array[T, N]

    class MyClass:

        ...

        def func(self, n):
            a, b = self.something_that_cannot_be_pythranized()

            if fp.is_pythranized:
                result = fp.use_pythranized_block("name_block")
            else:
                # pythran block (
                #     A a, b;
                #     int n
                # ) -> result

                result = a**n + b**n

            return self.another_func_that_cannot_be_pythranized(result)

Cached Just-In-Time compilation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using Just-In-Time compilation with the Ahead-Of-Time compiler Pythran is
possible with FluidPythran! It is really a "work in progress" so (i) it's buggy
and (ii) the API is not great, but it is a good start!

.. code :: python

    import numpy as np

    # pythran import numpy as numpy

    from fluidpythran import cachedjit, used_by_cachedjit

    @used_by_cachedjit("func1")
    def func0(a, b):
        return a + b

    @cachedjit()
    def func1(a, b):
        return np.exp(a) * b * func0(a, b)


Command :code:`# pythran class`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Just a NotImplemented idea! See https://bitbucket.org/fluiddyn/fluidpythran/issues/3/pythran-class

For simple methods only using simple attributes, if could be simple and *very*
useful to support this:

.. code :: python

    from fluidpythran import Type, NDim, Array, pythran_def

    import numpy as np

    T = Type(int, np.float64)
    N = NDim(1)

    A1 = Array[T, N]
    A2 = Array[float, N+1]

    class MyClass:

        arr0: A1
        arr1: A1
        arr2: A2

        def __init__(self, n, dtype=int):
            self.arr0 = np.zeros(n, dtype=dtype)
            self.arr1 = np.zeros(n, dtype=dtype)
            self.arr2 = np.zeros(n)

        @pythran_def
        def compute(self, alpha: int):
            tmp = (self.arr0 + self.arr1).mean()
            return tmp ** alpha * self.arr2

Make the Pythran files
----------------------

There is a command-line tool :code:`fluidpythran` which makes the associated
Pythran files from Python files with annotations and fluidpythran code.

There is also a function :code:`make_pythran_files` that can be used in a
setup.py like this:

.. code ::

    from pathlib import Path

    from fluidpythran.dist import make_pythran_files

    here = Path(__file__).parent.absolute()

    paths = ["fluidsim/base/time_stepping/pseudo_spect.py"]
    make_pythran_files([here / path for path in paths])

Note that FluidPythran never uses Pythran. Compiling the associated Pythran
file can be done if wanted (see for example how it is done in the example
package `example_package_fluidpythran
<https://bitbucket.org/fluiddyn/example_package_fluidpythran>`_ or in
`fluidsim's setup.py
<https://bitbucket.org/fluiddyn/fluidsim/src/default/setup.py>`_).

License
-------

FluidDyn is distributed under the CeCILL-B_ License, a BSD compatible
french license.

.. _CeCILL-B: http://www.cecill.info/index.en.html
