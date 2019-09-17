import cython

import numpy as np
cimport numpy as np

ctypedef fused __row_sum_arr:
   np.ndarray[np.int64_t, ndim=2]

ctypedef fused __row_sum_columns:
   np.ndarray[np.int32_t, ndim=1]

cpdef row_sum(__row_sum_arr arr, __row_sum_columns columns)

ctypedef fused __row_sum_loops_arr:
   np.int64_t[:, :]

ctypedef fused __row_sum_loops_columns:
   np.int32_t[:]

@cython.locals(i=np.int32_t, j=np.int32_t, sum_=np.int64_t, res=np.int64_t[:])
cpdef row_sum_loops(__row_sum_loops_arr arr, __row_sum_loops_columns columns)
