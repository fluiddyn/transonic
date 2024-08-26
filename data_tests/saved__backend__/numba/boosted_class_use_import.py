# __protected__ from numba import njit
import numpy as np
from __ext__MyClass2__exterior_import_boost import func_import

# __protected__ @njit(cache=True, fastmath=True)


def __for_method__MyClass2__myfunc(self_attr0, self_attr1, arg):
    return self_attr1 + self_attr0 + np.abs(arg) + func_import()


def __code_new_method__MyClass2__myfunc():
    return "\n\ndef new_method(self, arg):\n    return backend_func(self.attr0, self.attr1, arg)\n\n"


def __transonic__():
    return "0.7.1"
