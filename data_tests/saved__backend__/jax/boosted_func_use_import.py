# __protected__ from jax import jit
import jax.numpy as np
from __ext__func__exterior_import_boost import func_import

# __protected__ @jit


def func(a, b):
    return (a * np.log(b)).max() + func_import()


# __protected__ @jit


def __transonic__():
    return "0.7.1"
