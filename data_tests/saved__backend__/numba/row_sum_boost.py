# __protected__ from numba import njit
import numpy as np

# __protected__ @njit


def row_sum_loops(arr, columns):
    # locals type annotations are used only for Cython
    res = np.empty(arr.shape[0], dtype=arr.dtype)
    for i in range(arr.shape[0]):
        sum_ = 0
        for j in range(columns.shape[0]):
            sum_ += arr[(i, columns[j])]
        res[i] = sum_
    return res


# __protected__ @njit


def row_sum_transpose(arr, columns):
    return arr.T[columns].sum(0)


__transonic__ = ("0.3.3",)
