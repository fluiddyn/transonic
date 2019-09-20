import numpy as np

from transonic.aheadoftime import modules_backends

from package_cythran.calcul import laplace
from package_cythran.util import func

laplace(np.ones((2, 2), dtype=np.int32))
func(1)
func(2.)

ts = modules_backends["pythran"]["package_cythran.calcul"]
assert ts.backend.name == "pythran"

ts = modules_backends["cython"]["package_cythran.util"]
assert ts.backend.name == "cython"

print("everything looks alright!")
