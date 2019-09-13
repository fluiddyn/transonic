import cython

import numpy as np
cimport numpy as np

# not supported, see: https://github.com/cython/cython/issues/754
ctypedef np.ndarray[np.float64_t, ndim=1] A

def mysum(A arr):
    cdef np.float64_t ret = arr.dtype.type(0)
    cdef cython.int i
    for i in range(arr.shape[0]):
        ret += arr[i]
    return ret