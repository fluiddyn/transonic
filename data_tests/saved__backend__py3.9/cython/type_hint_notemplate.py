try:
    import cython
except ImportError:
    from transonic_cl import cython


def compute(a, b, c, d, e):
    print(e)
    tmp = a + b
    if 1 and 2:
        tmp *= 2
    return tmp


__transonic__ = ("0.3.3",)
