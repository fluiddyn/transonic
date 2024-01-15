try:
    import cython
except ImportError:
    from transonic_cl import cython


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


__code_new_method__Myclass__func = """

def new_method(self, arg):
    return backend_func(self.attr, self.attr2, arg)

"""

__transonic__ = ("0.3.3",)
