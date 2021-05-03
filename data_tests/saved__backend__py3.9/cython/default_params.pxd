import cython

import numpy as np
cimport numpy as np

ctypedef fused __func__Unionstr_None:
   cython.str

cpdef func(cython.int a=*, __func__Unionstr_None b=*, cython.float c=*)
