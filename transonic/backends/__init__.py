"""Backends for different accelerators
======================================

.. autosummary::
   :toctree:

   pythran
   cython
   numba

Internal API
------------

.. autofunction:: make_backend_files

"""

from pathlib import Path
from typing import Iterable, Optional

from transonic.config import backend_default

from .pythran import PythranBackend
from .cython import CythonBackend
from .numba import NumbaBackend

backends = dict(
    pythran=PythranBackend(), cython=CythonBackend(), numba=NumbaBackend()
)


def make_backend_files(
    paths: Iterable[Path],
    force=False,
    log_level=None,
    mocked_modules: Optional[Iterable] = None,
    backend=backend_default,
):
    """Create Pythran files from a list of Python files"""
    backend = backends[backend]
    backend.make_backend_files(paths, force, log_level, mocked_modules)
