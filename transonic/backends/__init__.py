"""Backends for different accelerators
======================================

.. autosummary::
   :toctree:

   pythran

"""

from transonic.analyses import analyse_aot

from .pythran import PythranBackend
from .numba import NumbaBackend
from .cython import CythonBackend

backends = dict(
    pythran=PythranBackend(), numba=NumbaBackend(), cython=CythonBackend()
)
