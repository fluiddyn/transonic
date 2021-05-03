import cython

import numpy as np
cimport numpy as np

cpdef block0(np.ndarray[np.float_t, ndim=2] a, np.ndarray[np.float_t, ndim=2] b, cython.int n)

cpdef block1(np.ndarray[np.float_t, ndim=2] a, np.ndarray[np.float_t, ndim=2] b, cython.int n)
