def compute(a, b, c, d, e):
    print(e)
    tmp = a + b
    return (tmp > 1) and (tmp > 2)


# pythran export __transonic__
__transonic__ = ("0.2.4",)
