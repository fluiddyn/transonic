import cython

import numpy as np
cimport numpy as np

ctypedef fused __rk2_step0_state_spect_n12:
   np.ndarray[np.complex128_t, ndim=3]

ctypedef fused __rk2_step0_state_spect:
   np.ndarray[np.complex128_t, ndim=3]

ctypedef fused __rk2_step0_tendencies_n:
   np.ndarray[np.complex128_t, ndim=3]

ctypedef fused __rk2_step0_diss2:
   np.ndarray[np.float64_t, ndim=2]

ctypedef fused __rk2_step0_dt:
   cython.float

cpdef rk2_step0(__rk2_step0_state_spect_n12 state_spect_n12, __rk2_step0_state_spect state_spect, __rk2_step0_tendencies_n tendencies_n, __rk2_step0_diss2 diss2, __rk2_step0_dt dt)
