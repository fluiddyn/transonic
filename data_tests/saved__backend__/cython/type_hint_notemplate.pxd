import cython

import numpy as np
cimport numpy as np

ctypedef fused __compute_a:
   np.ndarray[np.complex128_t, ndim=3]
   np.ndarray[np.complex128_t, ndim=1]
   np.ndarray[np.int_t, ndim=3]
   np.ndarray[np.int_t, ndim=1]

ctypedef fused __compute_b:
   np.ndarray[np.complex128_t, ndim=3]
   np.ndarray[np.complex128_t, ndim=1]
   np.ndarray[np.int_t, ndim=3]
   np.ndarray[np.int_t, ndim=1]

ctypedef fused __compute_c:
   np.complex128_t
   cython.int

ctypedef fused __compute_d:
   np.ndarray[np.complex128_t, ndim=3]
   np.ndarray[np.complex128_t, ndim=1]
   np.ndarray[np.float32_t, ndim=4]
   np.ndarray[np.float32_t, ndim=2]
   np.ndarray[np.int_t, ndim=3]
   np.ndarray[np.int_t, ndim=1]

ctypedef fused __compute_e:
   cython.str

cpdef compute(__compute_a a, __compute_b b, __compute_c c, __compute_d d, __compute_e e)
