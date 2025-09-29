# __protected__ from jax import jit
# __protected__ @jit


def gen_seq(dtype, seq_type, n):
    return seq_type(map(dtype, range(n)))


def __transonic__():
    return "0.7.3"
