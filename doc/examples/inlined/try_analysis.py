from transonic import boost


@boost
def f():
    pass


@boost(inline=1)
def f():
    pass


def f1():
    pass


def f2():
    pass


f1_ = boost(f1)
f1_ = boost(inline=1)(f1)


# decor = boost(inline=1)
# f1_ = decor(f1)
# f2_ = decor(f2)
