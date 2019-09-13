import cython

import numpy as np
cimport numpy as np

ctypedef fused T0:
   np.complex128_t
   np.float64_t

ctypedef T0[:] A


@cython.locals(ret=A, i=cython.int)
cpdef mysum(A arr)
