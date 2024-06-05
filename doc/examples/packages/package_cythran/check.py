import numpy as np
from numba.targets.registry import CPUDispatcher
from package_cythran.calcul import laplace
from package_cythran.other import func_numba
from package_cythran.util import func

from transonic.aheadoftime import modules_backends

laplace(np.ones((2, 2), dtype=np.int32))
func(1)
func(2.0)

ts = modules_backends["pythran"]["package_cythran.calcul"]
assert ts.backend.name == "pythran"

ts = modules_backends["cython"]["package_cythran.util"]
assert ts.backend.name == "cython"

ts = modules_backends["numba"]["package_cythran.other"]
assert ts.backend.name == "numba"

assert isinstance(func_numba, CPUDispatcher)

print("everything looks alright!")
