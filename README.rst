FluidPythran: use Pythran in non-pythranizable code
===================================================

|release| |coverage|

.. |release| image:: https://img.shields.io/pypi/v/fluidpythran.svg
   :target: https://pypi.python.org/pypi/fluidpythran/
   :alt: Latest version

.. |coverage| image:: https://codecov.io/bb/fluiddyn/fluidpythran/branch/default/graph/badge.svg
   :target: https://codecov.io/bb/fluiddyn/fluidpythran/branch/default/
   :alt: Code coverage


.. warning ::

   FluidPythran is still just a prototype. Remarks and suggestions are very
   welcome.

   FluidPythran just starts to be used in `FluidSim
   <https://bitbucket.org/fluiddyn/fluidsim>`_ (for example in `this file
   <https://bitbucket.org/fluiddyn/fluidsim/src/c0e170ea7c68f2abc4b0f7749b1c89df79db6573/fluidsim/base/time_stepping/pseudo_spect.py>`_).

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

With FluidPythran, we try to overcome these limitations. FluidPythran provides
few supplementary Pythran commands and a tiny Python API to define Pythran
functions without writing the Pythran modules. The code of the numerical
kernels can stay in the modules and in the classes where they were written. The
Pythran files (i.e. the files compiled by Pythran), which are usually written
by the user, are produced automatically by FluidPythran.

**Implementation detail:** For each Python file using FluidPythran, an
associated Pythran file is created in a directory :code:`_pythran`. For
example, for a Python file :code:`foo.py`, the associated file would be
:code:`_pythran/_foo.py`.

At run time, FluidPythran replaces the Python functions (and blocks) by their
versions in the Pythran files.

Let's stress again that codes using FluidPythran work fine without Pythran!

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

Command :code:`# pythran class`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Just a NotImplemented idea! See https://bitbucket.org/fluiddyn/fluidpythran/issues/3/pythran-class

For simple methods only using simple attributes, if could be simple and useful
to support this:

.. code :: python

    from fluidpythran import pythran_class

    import numpy as np

    @pythran_class
    class MyClass:
        # pythran class (
        #     int[] or float[]: arr0, arr1;
        #     float[][]: arr2
        # )

        def __init__(self, n, dtype=int):
            self.arr0 = np.zeros(n, dtype=dtype)
            self.arr1 = np.zeros(n, dtype=dtype)
            self.arr2 = np.zeros(n)

        # pythran def compute(object, float)

        def compute(self, alpha):
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
