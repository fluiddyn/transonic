cimport cython

cdef inline int add(int a, int b) nogil

@cython.locals(n=int, i=int, result=int)
cpdef use_add(int n)
