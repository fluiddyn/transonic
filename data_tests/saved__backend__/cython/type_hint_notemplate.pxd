import cython

import numpy as np
cimport numpy as np

ctypedef fused __compute__Array_TypeIint_complex128I_NDimI1_3I:
   np.ndarray[np.complex128_t, ndim=1]
   np.ndarray[np.complex128_t, ndim=3]
   np.ndarray[np.int_t, ndim=1]
   np.ndarray[np.int_t, ndim=3]

ctypedef fused __compute__TypeIint_complex128I:
   cython.int
   np.complex128_t

ctypedef fused __compute__UnionArray_TypeIint_complex128I_NDimI1_3I_Array_float32_NDimI1_3Ip1:
   np.ndarray[np.complex128_t, ndim=1]
   np.ndarray[np.complex128_t, ndim=3]
   np.ndarray[np.float32_t, ndim=2]
   np.ndarray[np.float32_t, ndim=4]
   np.ndarray[np.int_t, ndim=1]
   np.ndarray[np.int_t, ndim=3]

cpdef compute(__compute__Array_TypeIint_complex128I_NDimI1_3I a, __compute__Array_TypeIint_complex128I_NDimI1_3I b, __compute__TypeIint_complex128I c, __compute__UnionArray_TypeIint_complex128I_NDimI1_3I_Array_float32_NDimI1_3Ip1 d, cython.str e)
