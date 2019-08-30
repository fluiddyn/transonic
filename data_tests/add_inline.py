from transonic import boost

T = int


@boost(inline=True)
def add(a: T, b: T) -> T:
    return a + b


@boost
def use_add(n: int = 10000):
    tmp: T = 0
    _: T
    for _ in range(n):
        tmp = add(tmp, 1)
    return tmp
