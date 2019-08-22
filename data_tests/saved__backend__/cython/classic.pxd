import cython

import numpy as np
cimport numpy as np

ctypedef fused __func_a:
   np.float_t[:,:]
   np.int_t[:,:]

ctypedef fused __func_b:
   np.float_t[:,:]

cpdef func(__func_a a, __func_b b)
