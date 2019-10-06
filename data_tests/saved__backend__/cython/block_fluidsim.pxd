import cython

import numpy as np
cimport numpy as np

cpdef rk2_step0(np.ndarray[np.complex128_t, ndim=3] state_spect_n12, np.ndarray[np.complex128_t, ndim=3] state_spect, np.ndarray[np.complex128_t, ndim=3] tendencies_n, np.ndarray[np.float64_t, ndim=2] diss2, cython.float dt)
