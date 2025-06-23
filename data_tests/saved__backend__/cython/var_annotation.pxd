import cython

import numpy as np
cimport numpy as np

@cython.locals(approved_matches_ray=dict)
cpdef kernel_make_approved_matches__min_distance_matches_1ray(list candidates)
