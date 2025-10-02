import cython

import numpy as np
cimport numpy as np

ctypedef fused __gen_seq__Literal_int_float:
   object

ctypedef fused __gen_seq__Literal_list_set:
   object

cpdef gen_seq(__gen_seq__Literal_int_float dtype, __gen_seq__Literal_list_set seq_type, cython.int n)
