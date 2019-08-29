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

    from time import time
    from timeit import timeit

    n = 100000
    t0 = time()
    assert n == use_add(n)
    duration1 = time() - t0
    duration = 2
    number = max(10, int(round(duration / duration1)))
    print(
        f"{timeit('use_add(n)', globals=locals(), number=number)/number: .2e} s"
    )
