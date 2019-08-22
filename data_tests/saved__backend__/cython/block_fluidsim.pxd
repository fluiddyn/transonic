import cython

import numpy as np
cimport numpy as np

ctypedef fused __rk2_step0_state_spect_n12:
   np.complex128_t[:,:,:]

ctypedef fused __rk2_step0_state_spect:
   np.complex128_t[:,:,:]

ctypedef fused __rk2_step0_tendencies_n:
   np.complex128_t[:,:,:]

ctypedef fused __rk2_step0_diss2:
   np.float64_t[:,:]

ctypedef fused __rk2_step0_dt:
   cython.float

cpdef rk2_step0(__rk2_step0_state_spect_n12 state_spect_n12, __rk2_step0_state_spect state_spect, __rk2_step0_tendencies_n tendencies_n, __rk2_step0_diss2 diss2, __rk2_step0_dt dt)
