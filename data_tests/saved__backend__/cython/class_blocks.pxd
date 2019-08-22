import cython

import numpy as np
cimport numpy as np

ctypedef fused __block0_a:
   np.float_t[:,:]
   np.float_t[:,:,:]

ctypedef fused __block0_b:
   np.float_t[:,:]
   np.float_t[:,:,:]

ctypedef fused __block0_n:
   cython.int

cpdef block0(__block0_a a, __block0_b b, __block0_n n)

ctypedef fused __block1_a:
   np.float_t[:,:]
   np.float_t[:,:,:]

ctypedef fused __block1_b:
   np.float_t[:,:]
   np.float_t[:,:,:]

ctypedef fused __block1_n:
   cython.int

cpdef block1(__block1_a a, __block1_b b, __block1_n n)
