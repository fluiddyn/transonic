def add(a, b):
    return a + b


def use_add(n=10000):
    tmp = 0
    for _ in range(n):
        tmp = add(tmp, 1)
    return tmp


__transonic__ = ("0.3.2",)
