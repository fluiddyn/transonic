# __protected__ from jax import jit
import jax.numpy as np

# __protected__ @jit


def func(a, b):
    return (a * np.log(b)).max()


__transonic__ = ("0.6.3+editable",)
