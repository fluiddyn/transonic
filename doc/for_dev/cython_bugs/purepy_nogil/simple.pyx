# cython: language_level=3
import cython

cpdef inline cython.int add(cython.int a, cython.int b) nogil:
    return a + b

cpdef use_add(cython.int n):
    cdef Py_ssize_t i
    cdef cython.int result = 1
    with cython.nogil:
        for i in range(n):
            result = add(result, result)
    return result