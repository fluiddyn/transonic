# cython: language_level=3

import cython

@cython.ccall
@cython.inline
@cython.returns(cython.int)
@cython.locals(a=cython.int, b=cython.int)
@cython.nogil
def add(a, b):
    return a + b

@cython.ccall
@cython.locals(n=cython.int, i=Py_ssize_t, result=cython.int)
def use_add(n):
    result = 1
    with cython.nogil:
        for i in range(n):
            result = add(result, result)
    return result
