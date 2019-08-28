import numpy as np

from transonic import jit


@jit(native=True, xsimd=True)
def row_sum_loops(arr, columns):
    res = np.empty(arr.shape[0], dtype=arr.dtype)
    for i in range(arr.shape[0]):
        sum_ = 0
        for j in range(columns.shape[0]):
            sum_ += arr[i, columns[j]]
        res[i] = sum_
    return res


@jit(native=True, xsimd=True)
def row_sum_transpose(arr, columns):
    return arr.T[columns].sum(0)


if __name__ == "__main__":

    from transonic import wait_for_all_extensions

    from util import check, bench

    functions = [row_sum_loops, row_sum_transpose]
    arr = np.arange(1_000_000).reshape(1_000, 1_000)
    columns = np.arange(1, 1000, 2)

    check(functions, arr, columns)
    wait_for_all_extensions()
    check(functions, arr, columns)
    bench(functions, arr, columns)
