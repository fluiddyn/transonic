from transonic import jit, wait_for_all_extensions


@jit
def func_dict(d: "str: float dict"):
    return d.popitem()


d = {"a": 0, "b": 1}
result = func_dict(d)

wait_for_all_extensions()

d1 = {"a": 0, "b": 1}
result1 = func_dict(d1)

assert d == d1
assert result == result1
