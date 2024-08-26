# __protected__ from jax import jit
# __protected__ @jit


def block0(a, b, n):
    # transonic block (
    #     A a; A1 b;
    #     int n
    # )
    # transonic block (
    #     int[:] a, b;
    #     float n
    # )
    result = a**2 + b.mean() ** 3 + n
    return result


# __protected__ @jit


def arguments_blocks():
    return {"block0": ["a", "b", "n"]}


# __protected__ @jit


def __transonic__():
    return "0.7.1"
