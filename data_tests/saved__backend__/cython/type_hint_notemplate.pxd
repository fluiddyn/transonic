import cython

import numpy as np
cimport numpy as np

ctypedef fused __compute_a:
   np.complex128_t[:, :, :]
   np.complex128_t[:]
   np.int_t[:, :, :]
   np.int_t[:]

ctypedef fused __compute_b:
   np.complex128_t[:, :, :]
   np.complex128_t[:]
   np.int_t[:, :, :]
   np.int_t[:]

ctypedef fused __compute_c:
   np.complex128
   cython.int

ctypedef fused __compute_d:
   np.complex128_t[:]
   np.float32_t[:, :]
   np.float32_t[:, :, :, :]
   np.int_t[:, :, :]
   np.int_t[:]
   np.complex128_t[:, :, :]

ctypedef fused __compute_e:
   cython.str

cpdef compute(__compute_a a, __compute_b b, __compute_c c, __compute_d d, __compute_e e)
