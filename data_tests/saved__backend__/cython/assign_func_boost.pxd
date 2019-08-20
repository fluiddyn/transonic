import cython

import numpy as np
cimport numpy as np

ctypedef fused __func_x:
   cython.int

cpdef func(__func_x x)
