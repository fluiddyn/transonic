try:
    import cython
except ImportError:
    from transonic_cl import cython


def func(a=1, b=None, c=1.0):
    print(b)
    return a + c


__transonic__ = ("0.4.0",)
