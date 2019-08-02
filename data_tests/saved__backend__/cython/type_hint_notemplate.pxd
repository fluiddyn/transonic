ctypedef fused __compute_a:
   int[:, :, :]
   int[:]
   complex128[:]
   complex128[:, :, :]
ctypedef fused __compute_b:
   int[:, :, :]
   int[:]
   complex128[:]
   complex128[:, :, :]
ctypedef fused __compute_c:
   complex128
   int
ctypedef fused __compute_d:
   int[:]
   complex128[:, :, :]
   float32[:, :, :, :]
   float32[:, :]
   int[:, :, :]
   complex128[:]
ctypedef fused __compute_e:
   str
cdef compute(__compute_a a, __compute_b b, __compute_c c, __compute_d d, __compute_e e)
