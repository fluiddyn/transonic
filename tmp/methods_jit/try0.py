

from fluidpythran.transpiler import produce_new_code_class_func


def boost(obj):
    return obj


def cachedjit(method):
    return method


@boost
class MyClass:
    def __init__(self):
        self.attr0 = self.attr1 = 1

    @cachedjit
    def myfunc(self, arg):
        return self.attr1 + self.attr0 + arg


python_code = produce_new_code_class_func(MyClass, "myfunc", jit=True)
