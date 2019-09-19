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
from typing import Iterable
import inspect

from transonic.config import backend_default
from transonic.util import get_module_name

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
    backend_name = backend_name.lower()
    frame = inspect.stack()[1]
    module_name = get_module_name(frame)
    if backend_name not in backends.keys():
        raise ValueError(f"Bad backend value ({backend_name})")
    backend_default_modules[module_name] = backend_name


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
