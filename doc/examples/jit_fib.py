from transonic import jit, wait_for_all_extensions


@jit
def fib(n: int):
    """fibonacci"""
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


@jit
def use_fib():
    return [fib(n) for n in [1, 3, 5]]


fib2 = fib(2)
result = use_fib()
wait_for_all_extensions()
assert fib2 == fib(2)
assert result == use_fib()
