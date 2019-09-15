import cython

ctypedef fused A:
    int[:]
    float[:]

@cython.locals(arr=A)
cpdef func(A arg)
