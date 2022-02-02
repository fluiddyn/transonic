try:
    import cython
except ImportError:
    from transonic_cl import cython


def func(x):
    return x**2


__transonic__ = ("0.3.3",)
