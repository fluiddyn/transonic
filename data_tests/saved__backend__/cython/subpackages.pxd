import cython

import numpy as np
cimport numpy as np

cpdef test_np_fft(np.ndarray[np.float_t, ndim=1] u)

cpdef test_np_linalg_random(np.ndarray[np.float_t, ndim=2] u)

cpdef test_sp_special(cython.int v, cython.float x)
