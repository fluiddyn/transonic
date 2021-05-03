import cython

import numpy as np
cimport numpy as np

cpdef row_sum(np.ndarray[np.int64_t, ndim=2] arr, np.ndarray[np.int32_t, ndim=1] columns)

@cython.locals(i=np.int32_t, j=np.int32_t, sum_=np.int64_t, res=np.int64_t[:])
cpdef row_sum_loops(np.int64_t[:, :] arr, np.int32_t[:] columns)
