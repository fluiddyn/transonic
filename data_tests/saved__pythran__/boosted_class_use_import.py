import numpy as np
from __MyClass2__exterior_import_boost import func_import


# pythran export __for_method__MyClass2__myfunc(int, int, int)


def __for_method__MyClass2__myfunc(self_attr0, self_attr1, arg):
    return ((self_attr1 + self_attr0) + np.abs(arg)) + func_import()


# pythran export __code_new_method__MyClass2__myfunc

__code_new_method__MyClass2__myfunc = """

def new_method(self, arg):
    return pythran_func(self.attr0, self.attr1, arg)

"""

# pythran export __transonic__
__transonic__ = ("0.2.3",)