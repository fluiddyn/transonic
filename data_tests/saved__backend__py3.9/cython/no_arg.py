try:
    import cython
except ImportError:
    from transonic_cl import cython


def func():
    return 1


def func2():
    return 1


__transonic__ = ("0.3.3",)
