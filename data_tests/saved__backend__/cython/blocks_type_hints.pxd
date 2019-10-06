import cython

import numpy as np
cimport numpy as np

ctypedef fused __block0__Array_Tfloat_complex_NDim1_2p1:
   np.ndarray[np.complex_t, ndim=2]
   np.ndarray[np.complex_t, ndim=3]
   np.ndarray[np.float_t, ndim=2]
   np.ndarray[np.float_t, ndim=3]

ctypedef fused __block0__Array_Tfloat_complex_NDim1_2:
   np.ndarray[np.complex_t, ndim=1]
   np.ndarray[np.complex_t, ndim=2]
   np.ndarray[np.float_t, ndim=1]
   np.ndarray[np.float_t, ndim=2]

cpdef block0(__block0__Array_Tfloat_complex_NDim1_2 a, __block0__Array_Tfloat_complex_NDim1_2p1 b, cython.int n)
