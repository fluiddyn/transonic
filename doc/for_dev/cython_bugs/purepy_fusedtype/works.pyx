import cython

import numpy as np
cimport numpy as np

ctypedef fused A:
    np.int_t[:]
    np.float_t[:]

cpdef func(A arg):
    cdef A arr = np.empty_like(arg)
    return arr
