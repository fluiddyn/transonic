"""Backends for different accelerators
======================================

.. autosummary::
   :toctree:

   pythran
   cython
   numba

"""

from .pythran import PythranBackend
from .cython import CythonBackend
from .numba import NumbaBackend

backends = dict(
    pythran=PythranBackend(), cython=CythonBackend(), numba=NumbaBackend()
)
