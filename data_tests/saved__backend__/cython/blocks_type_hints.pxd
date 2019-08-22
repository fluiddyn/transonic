import cython

import numpy as np
cimport numpy as np

ctypedef fused __block0_a:
   np.complex_t[:, :]
   np.complex_t[:]
   np.float_t[:, :]
   np.float_t[:]
   np.int_t[:]

ctypedef fused __block0_b:
   np.complex_t[:, :, :]
   np.complex_t[:, :]
   np.float_t[:, :, :]
   np.float_t[:, :]
   np.int_t[:]

ctypedef fused __block0_n:
   cython.float
   cython.int

cpdef block0(__block0_a a, __block0_b b, __block0_n n)
