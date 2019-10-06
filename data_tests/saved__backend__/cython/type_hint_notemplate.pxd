import cython

import numpy as np
cimport numpy as np

ctypedef fused __compute__Array_Tint_complex128_NDim1_3:
   np.ndarray[np.complex128_t, ndim=1]
   np.ndarray[np.complex128_t, ndim=3]
   np.ndarray[np.int_t, ndim=1]
   np.ndarray[np.int_t, ndim=3]

ctypedef fused __compute__Tint_complex128:
   cython.int
   np.complex128_t

ctypedef fused __compute__UnionArray_Tint_complex128_NDim1_3_Array_float32_NDim1_3p1:
   np.ndarray[np.complex128_t, ndim=1]
   np.ndarray[np.complex128_t, ndim=3]
   np.ndarray[np.float32_t, ndim=2]
   np.ndarray[np.float32_t, ndim=4]
   np.ndarray[np.int_t, ndim=1]
   np.ndarray[np.int_t, ndim=3]

cpdef compute(__compute__Array_Tint_complex128_NDim1_3 a, __compute__Array_Tint_complex128_NDim1_3 b, __compute__Tint_complex128 c, __compute__UnionArray_Tint_complex128_NDim1_3_Array_float32_NDim1_3p1 d, cython.str e)
