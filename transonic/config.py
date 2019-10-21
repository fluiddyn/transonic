"""Configuration
================

Transonic is sensible to the environment variables:

- :code:`TRANSONIC_DIR` can be set to control where the cached files are
  saved.

- :code:`TRANSONIC_COMPILE_AT_IMPORT` can be set to enable a mode for which
  Transonic compiles at import time the Pythran file associated with the
  imported module. This behavior can also be triggered programmatically by using
  the function :code:`set_compile_at_import`.

- :code:`TRANSONIC_NO_REPLACE` can be set to disable all code replacements.
  This is useful only when measuring code coverage.

- :code:`FLUID_COMPILE_JIT` can be set to false to disable the
  compilation of jited functions. This can be useful for unittests.

Bye the way, for performance, it is important to configure Pythran with a file
`~/.pythranrc
<https://pythran.readthedocs.io/en/latest/MANUAL.html#customizing-your-pythranrc>`_:

For Linux, I use:

.. code:: raw

    [pythran]
    complex_hook = True

    [compiler]
    CXX=clang++-6.0
    CC=clang-6.0
    blas=openblas

User API
--------

.. autofunction:: set_backend

"""

import os
from pathlib import Path
from distutils.util import strtobool
from warnings import warn

path_root = Path(os.environ.get("TRANSONIC_DIR", Path.home() / ".transonic"))

has_to_replace = not strtobool(os.environ.get("TRANSONIC_NO_REPLACE", "0"))

backend_default = "pythran"
backend_set_by_user = False


def set_backend(backend: str):
    """Set the "global variable" backend_default"""

    backend = backend.lower()
    supported_backends = ["pythran", "cython", "numba", "python"]
    if backend not in supported_backends:
        raise ValueError(f"backend {backend} not supported")

    global backend_default, backend_set_by_user

    backend_default = backend
    backend_set_by_user = True

    # warning: this import has to be here!
    from transonic.util import can_import_accelerator

    if not can_import_accelerator(backend):
        warn(f'Backend set to "{backend}" but accelerator not importable')


try:
    _backend = os.environ["TRANSONIC_BACKEND"]
except KeyError:
    pass
else:
    set_backend(_backend)
