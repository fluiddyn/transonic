import cython

import numpy as np
cimport numpy as np

ctypedef fused __block0_a:
   np.ndarray[np.complex_t, ndim=2]
   np.ndarray[np.complex_t, ndim=1]
   np.ndarray[np.float_t, ndim=2]
   np.ndarray[np.float_t, ndim=1]
   np.ndarray[np.int_t, ndim=1]

ctypedef fused __block0_b:
   np.ndarray[np.complex_t, ndim=3]
   np.ndarray[np.complex_t, ndim=2]
   np.ndarray[np.float_t, ndim=3]
   np.ndarray[np.float_t, ndim=2]
   np.ndarray[np.int_t, ndim=1]

ctypedef fused __block0_n:
   cython.float
   cython.int

cpdef block0(__block0_a a, __block0_b b, __block0_n n)
