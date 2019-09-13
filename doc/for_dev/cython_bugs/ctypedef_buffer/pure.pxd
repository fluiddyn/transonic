import cython

import numpy as np
cimport numpy as np

ctypedef fused T0:
   np.complex128_t
   np.float64_t

@cython.locals(ret=T0, i=cython.int)
cpdef mysum(np.ndarray[T0, ndim=1] arr)
