from transonic import boost, jit, set_backend_for_this_module, Transonic

set_backend_for_this_module("python")

ts = Transonic()


@boost
def func():
    return 0


@jit
def func_jit():
    return 0
