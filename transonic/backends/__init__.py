"""Backends for different accelerators
======================================

.. autosummary::
   :toctree:

   pythran

"""

from transonic.analyses import analyse_aot

from .pythran import PythranBackend
from .cython import CythonBackend

backends = dict(pythran=PythranBackend(), cython=CythonBackend())
