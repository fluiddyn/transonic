from transonic import jit


@jit
def func(a,b):
    return a+b

func(0,1)