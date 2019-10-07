cdef cython.int add(cython.int a, cython.int b)

@cython.locals(n=cython.int, i=Py_ssize_t, result=cython.int)
cpdef use_add(cython.int n)