
ctypedef fused A:
    int[:]
    float[:]

cpdef func(A arg):
    cdef A arr = arg
    return arr
