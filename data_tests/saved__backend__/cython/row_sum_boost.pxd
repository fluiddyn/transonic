import cython

import numpy as np
cimport numpy as np

ctypedef fused __row_sum_loops_arr:
   np.ndarray[np.int_t, ndim=2]

ctypedef fused __row_sum_loops_columns:
   np.ndarray[np.int_t, ndim=1]

@cython.locals(i=cython.int, j=cython.int, sum_=cython.int, res=np.int_t[:])
cpdef row_sum_loops(__row_sum_loops_arr arr, __row_sum_loops_columns columns)

ctypedef fused __row_sum_transpose_arr:
   np.ndarray[np.int_t, ndim=2]

ctypedef fused __row_sum_transpose_columns:
   np.ndarray[np.int_t, ndim=1]

cpdef row_sum_transpose(__row_sum_transpose_arr arr, __row_sum_transpose_columns columns)
