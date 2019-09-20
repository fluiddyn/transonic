from transonic import boost, set_backend_for_this_module

set_backend_for_this_module("numba")


@boost
def func_numba(a):
    return a ** 2
