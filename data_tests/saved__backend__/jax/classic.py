# __protected__ from jax import jit
import jax.numpy as np

# __protected__ @jit


def func(a, b):
    return (a * np.log(b)).max()


def __transonic__():
    return "0.7.1"
