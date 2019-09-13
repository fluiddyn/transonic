import cython

import numpy as np
cimport numpy as np

ctypedef fused T0:
   np.complex128_t
   np.float64_t

def mysum(np.ndarray[T0, ndim=1] arr):
    cdef T0 ret = arr.dtype.type(0)
    cdef cython.int i
    for i in range(arr.shape[0]):
        ret += arr[i]
    return ret