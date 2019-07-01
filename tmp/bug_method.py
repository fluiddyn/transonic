from transonic import jit, boost
from for_test_exterior_import_jit import fib
import numpy as np


def func0(a):
    return 2 * a

func0 = jit(func0)
fib = jit(fib)

@jit
def jitted_use_func0():
    return func0(1)


@jit
def jitted_use_fib():
    return fib(1)

# @boost
# class MyClass2:
#     def __init__(self):
#         self.attr0 = self.attr1 = 1

#     @jit()
#     def myfunc(self, arg):
#         return self.attr1 + self.attr0 + np.abs(arg) + func0(1)
#     def check(self):
#         assert self.myfunc(1) == 5


if __name__ == "__main__":

    jitted_use_func0()
    jitted_use_fib()


    
