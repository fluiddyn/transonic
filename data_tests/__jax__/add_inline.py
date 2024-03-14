# __protected__ from jax import jit
# __protected__ @jit


def add(a, b):
    return a + b


# __protected__ @jit


def use_add(n=10000):
    tmp = 0
    for _ in range(n):
        tmp = add(tmp, 1)
    return tmp


__transonic__ = ("0.6.3+editable",)
