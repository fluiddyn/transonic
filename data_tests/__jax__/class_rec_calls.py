# __protected__ from jax import jit
# __protected__ @jit


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


__code_new_method__Myclass__func = "\n\ndef new_method(self, arg):\n    return backend_func(self.attr, self.attr2, arg)\n\n"
__transonic__ = ("0.6.3+editable",)
