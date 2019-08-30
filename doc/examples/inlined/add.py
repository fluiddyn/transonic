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


if __name__ == "__main__":

    from transonic.util import timeit

    n = 100000
    assert n == use_add(n)

    print(f"{timeit('use_add(n)', globals=locals()): .2e} s")
