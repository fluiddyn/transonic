"""Configuration
================

FluidPythran is sensible to the environment variables:

- :code:`FLUIDPYTHRAN_DIR` can be set to control where the cached files are
  saved.

- :code:`PYTHRANIZE_AT_IMPORT` can be set to enable a mode for which
  FluidPythran compiles at import time the Pythran file associated with the
  imported module. This behavior can also be triggered programmatically by using
  the function :code:`set_pythranize_at_import`.

- :code:`FLUIDPYTHRAN_NO_REPLACE` can be set to disable all code replacements.
  This is useful only when measuring code coverage.

- :code:`FLUID_COMPILE_CACHEDJIT` can be set to false to disable the
  compilation of cachedjited functions. This can be useful for unittests.

Bye the way, for performance, it is important to configure Pythran with a file
`~/.pythranrc
<https://pythran.readthedocs.io/en/latest/MANUAL.html#customizing-your-pythranrc>`_:

For Linux, I use:

.. code::

    [pythran]
    complex_hook = True

    [compiler]
    CXX=clang++-6.0
    CC=clang-6.0
    blas=openblas

"""

import os
from pathlib import Path
from distutils.util import strtobool

path_root = Path(
    os.environ.get("FLUIDPYTHRAN_DIR", Path.home() / ".fluidpythran")
)

has_to_replace = not strtobool(os.environ.get("FLUIDPYTHRAN_NO_REPLACE", "0"))