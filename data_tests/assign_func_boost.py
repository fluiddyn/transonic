from transonic import boost


def func(x: int):
    return x**2


def func2(x: int):
    return x**2


func_boosted = boost(func)
