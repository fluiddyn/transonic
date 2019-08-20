import cython

import numpy as np
cimport numpy as np

ctypedef fused __func_a:
   cython.float

ctypedef fused __func_b:
   cython.float

cpdef func(__func_a a, __func_b b)

ctypedef fused __func1_a:
   cython.int

ctypedef fused __func1_b:
   cython.float

cpdef func1(__func1_a a, __func1_b b)
