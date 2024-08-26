def __for_method__Myclass__func(self_attr, self_attr2, arg):
    if __for_method__Myclass__func(self_attr, self_attr2, arg - 1) < 1:
        return 1
    else:
        a = __for_method__Myclass__func(
            self_attr, self_attr2, arg - 1
        ) * __for_method__Myclass__func(self_attr, self_attr2, arg - 1)
        return (
            a
            + self_attr * self_attr2 * arg
            + __for_method__Myclass__func(self_attr, self_attr2, arg - 1)
        )


def __code_new_method__Myclass__func():
    return """

def new_method(self, arg):
    return backend_func(self.attr, self.attr2, arg)

"""


def __transonic__():
    return "0.7.1"
