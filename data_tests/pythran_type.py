from typing import Literal

from transonic import boost


@boost
def gen_seq(dtype: Literal[int, float], seq_type: Literal[list, set], n: int):
    return seq_type(map(dtype, range(n)))
