import cython

import numpy as np
cimport numpy as np

cpdef block0(complex[:, :], complex[:, :, :], int)

cpdef block0(complex[:], complex[:, :], int)

cpdef block0(float[:, :], float[:, :, :], int)

cpdef block0(float[:], float[:, :], int)

cpdef block0(int[:], int[:], float)
