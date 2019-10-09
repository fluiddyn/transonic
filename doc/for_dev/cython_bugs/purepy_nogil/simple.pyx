# cython: language_level=3
import cython

cpdef inline int add(int a, int b) nogil:
    return a + b

cpdef use_add(cython.int n):
    cdef int i
    cdef int result = 1
    with cython.nogil:
        for i in range(n):
            result = add(result, result)
    return result