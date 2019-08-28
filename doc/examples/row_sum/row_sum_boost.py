import numpy as np

from transonic import boost

T0 = "int[:, :]"
T1 = "int[:]"


@boost
def row_sum_loops(arr: T0, columns: T1):
    # locals type annotations are used only for Cython
    i: int
    j: int
    sum_: int
    res: "int[]" = np.empty(arr.shape[0], dtype=arr.dtype)
    for i in range(arr.shape[0]):
        sum_ = 0
        for j in range(columns.shape[0]):
            sum_ += arr[i, columns[j]]
        res[i] = sum_
    return res


@boost
def row_sum_transpose(arr: T0, columns: T1):
    return arr.T[columns].sum(0)


if __name__ == "__main__":

    from util import check, bench

    functions = [row_sum_loops, row_sum_transpose]
    arr = np.arange(1_000_000).reshape(1_000, 1_000)
    columns = np.arange(1, 1000, 2)

    check(functions, arr, columns)
    bench(functions, arr, columns)
