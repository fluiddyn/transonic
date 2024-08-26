try:
    import cython
except ImportError:
    from transonic_cl import cython


def func(x):
    return x**2


def __transonic__():
    return "0.7.1"
