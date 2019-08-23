# __protected__ from numba import njit
import numpy as np
from exterior_import_boost import func_import

# __protected__ @njit


def __for_method__MyClass2__myfunc(self_attr0, self_attr1, arg):
    return ((self_attr1 + self_attr0) + np.abs(arg)) + func_import()


__code_new_method__MyClass2__myfunc = "\n\ndef new_method(self, arg):\n    return backend_func(self.attr0, self.attr1, arg)\n\n"
__transonic__ = ("0.3.0.post0",)
