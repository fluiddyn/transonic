"""Backends for different accelerators
======================================

.. autosummary::
   :toctree:

   base
   base_jit
   for_classes

.. autosummary::
   :toctree:

   pythran
   cython
   numba
   py

Internal API
------------

.. autofunction:: make_backend_files

"""

from pathlib import Path
from typing import Iterable, Optional

from transonic.config import backend_default

from .py import PythonBackend
from .pythran import PythranBackend
from .cython import CythonBackend
from .numba import NumbaBackend

backends = dict(
    pythran=PythranBackend(),
    cython=CythonBackend(),
    numba=NumbaBackend(),
    python=PythonBackend(),
)


backend_default_modules = {}


def set_backend_for_this_module(backend_name):
    raise NotImplementedError


def get_backend_name_module(module_name):
    return backend_default_modules.get(module_name, backend_default)


def make_backend_files(
    paths: Iterable[Path],
    force=False,
    log_level=None,
    backend: str = backend_default,
):
    """Create Pythran files from a list of Python files"""
    backend = backends[backend]
    backend.make_backend_files(paths, force, log_level)
