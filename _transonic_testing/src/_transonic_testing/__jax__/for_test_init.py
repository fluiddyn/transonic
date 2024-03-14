# __protected__ from jax import jit
# __protected__ @jit


def func_tmp(arg):
    return arg**2


import jax.numpy as np

# __protected__ @jit


def func(a, b):
    i = 2
    c = 0.1 + i
    return a + b + c


# __protected__ @jit


def func0(a, b):
    return a + b


# __protected__ @jit


def func2(a, b):
    return a - func_tmp(b)


# __protected__ @jit


def func3(c):
    return c[0] + 1


# __protected__ @jit


def __for_method__Transmitter____call__(self_freq, inp):
    """My docstring"""
    return inp * np.exp(np.arange(len(inp)) * self_freq * 1j)


__code_new_method__Transmitter____call__ = (
    "\n\ndef new_method(self, inp):\n    return backend_func(self.freq, inp)\n\n"
)
# __protected__ @jit


def __for_method__Transmitter__other_func(self_freq):
    return 2 * self_freq


__code_new_method__Transmitter__other_func = (
    "\n\ndef new_method(self, ):\n    return backend_func(self.freq, )\n\n"
)
# __protected__ @jit


def block0(a, b, n):
    # transonic block (
    #     float a, b;
    #     int n
    # )
    result = 0.0
    for _ in range(n):
        result += a**2 + b**3
    return result


arguments_blocks = {"block0": ["a", "b", "n"]}
__transonic__ = ("0.6.3+editable",)
