ctypedef fused __func_a:
   float
ctypedef fused __func_b:
   float
cdef func(__func_a a, __func_b b)
ctypedef fused __func1_a:
   int
ctypedef fused __func1_b:
   float
cdef func1(__func1_a a, __func1_b b)
