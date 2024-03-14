# __protected__ from jax import jit
# __protected__ @jit


def func(a=1, b=None, c=1.0):
    print(b)
    return a + c


__transonic__ = ("0.6.3+editable",)
