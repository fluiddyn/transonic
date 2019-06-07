from transonic import jit


def func(x):
    return x ** 2


def func2(x):
    return x ** 2


func_jitted = jit(func)
