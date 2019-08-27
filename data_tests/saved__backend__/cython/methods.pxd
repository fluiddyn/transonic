import cython

import numpy as np
cimport numpy as np

ctypedef fused ____for_method__Transmitter____call___self_arr:
   np.ndarray[np.float_t, ndim=2]

ctypedef fused ____for_method__Transmitter____call___self_freq:
   cython.float

ctypedef fused ____for_method__Transmitter____call___inp:
   np.ndarray[np.float_t, ndim=1]

cpdef __for_method__Transmitter____call__(____for_method__Transmitter____call___self_arr self_arr, ____for_method__Transmitter____call___self_freq self_freq, ____for_method__Transmitter____call___inp inp)
