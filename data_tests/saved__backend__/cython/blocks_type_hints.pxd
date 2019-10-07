import cython

import numpy as np
cimport numpy as np

ctypedef fused __block0__Array_TypeIfloat_complexI_NDimI1_2Ip1:
   np.ndarray[np.complex_t, ndim=2]
   np.ndarray[np.complex_t, ndim=3]
   np.ndarray[np.float_t, ndim=2]
   np.ndarray[np.float_t, ndim=3]

ctypedef fused __block0__Array_TypeIfloat_complexI_NDimI1_2I:
   np.ndarray[np.complex_t, ndim=1]
   np.ndarray[np.complex_t, ndim=2]
   np.ndarray[np.float_t, ndim=1]
   np.ndarray[np.float_t, ndim=2]

cpdef block0(__block0__Array_TypeIfloat_complexI_NDimI1_2I a, __block0__Array_TypeIfloat_complexI_NDimI1_2Ip1 b, cython.int n)
