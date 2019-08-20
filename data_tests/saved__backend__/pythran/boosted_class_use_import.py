import numpy as np
from __ext__MyClass2__exterior_import_boost import func_import


def __for_method__MyClass2__myfunc(self_attr0, self_attr1, arg):
    return ((self_attr1 + self_attr0) + np.abs(arg)) + func_import()


__code_new_method__MyClass2__myfunc = """

def new_method(self, arg):
    return backend_func(self.attr0, self.attr1, arg)

"""

__transonic__ = ("0.3.0",)
