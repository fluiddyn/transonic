import cython

import numpy as np
cimport numpy as np

ctypedef fused __func_a:
   np.ndarray[np.float_t, ndim=2]
   np.ndarray[np.int_t, ndim=2]

ctypedef fused __func_b:
   np.ndarray[np.float_t, ndim=2]

cpdef func(__func_a a, __func_b b)
