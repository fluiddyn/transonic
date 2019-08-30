try:
    import cython
except ImportError:
    from transonic_cl import cython

import numpy as np


@cython.boundscheck(False)
@cython.wraparound(False)
def row_sum_loops(arr, columns):
    # locals type annotations are used only for Cython
    res = np.empty(arr.shape[0], dtype=arr.dtype)
    for i in range(arr.shape[0]):
        sum_ = 0
        for j in range(columns.shape[0]):
            sum_ += arr[(i, columns[j])]
        res[i] = sum_
    return res


def row_sum_transpose(arr, columns):
    return arr.T[columns].sum(0)


__transonic__ = ("0.3.3",)
