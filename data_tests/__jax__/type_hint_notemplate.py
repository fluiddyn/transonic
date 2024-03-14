# __protected__ from jax import jit
# __protected__ @jit


def compute(a, b, c, d, e):
    print(e)
    tmp = a + b
    if 1 and 2:
        tmp *= 2
    return tmp


__transonic__ = ("0.6.3+editable",)
