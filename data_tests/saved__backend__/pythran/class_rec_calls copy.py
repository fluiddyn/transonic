# pythran export __for_method__Myclass__func(int, int, int)


def __for_method__Myclass__func(self_attr, self_attr2, arg):
    if __for_method__Myclass__func(self_attr, self_attr2, (arg - 1)) < 1:
        return 1
    else:
        a = __for_method__Myclass__func(
            self_attr, self_attr2, (arg - 1)
        ) * __for_method__Myclass__func(self_attr, self_attr2, (arg - 1))
        return (
            a + ((self_attr * self_attr2) * arg)
        ) + __for_method__Myclass__func(self_attr, self_attr2, (arg - 1))


# pythran export __code_new_method__Myclass__func

__code_new_method__Myclass__func = """

def new_method(self, arg):
    return pythran_func(self.attr, self.attr2, arg)

"""

# pythran export __transonic__
__transonic__ = ("0.2.3",)
