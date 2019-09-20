import numpy as np

from transonic.aheadoftime import modules_backends

from package_simple.calcul import laplace
from package_simple.util import func

laplace(np.ones((2, 2), dtype=np.int32))
func(1)
func(2.)

modules = modules_backends["pythran"]

ts = modules["package_simple.calcul"]
assert ts.backend.name == "pythran"

ts = modules["package_simple.util"]
assert ts.backend.name == "pythran"

print("everything looks alright!")
