import cython

import numpy as np
cimport numpy as np

ctypedef fused A:
    np.int_t[:]
    np.float_t[:]

@cython.locals(arr=A)
cpdef func(A arg)
