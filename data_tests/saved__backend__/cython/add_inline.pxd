import cython

import numpy as np
cimport numpy as np

ctypedef fused __add_a:
   cython.int

ctypedef fused __add_b:
   cython.int

cpdef inline cython.int add(__add_a a, __add_b b)

ctypedef fused __use_add_n:
   cython.int

@cython.locals(tmp=cython.int, _=cython.int)

cpdef use_add(__use_add_n n=*)
