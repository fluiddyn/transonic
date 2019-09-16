import numpy as np

from transonic import boost, Array

MV1d = Array[np.int64, "1d", "memview"]
MV2d = Array[np.int64, "2d", "memview"]

A1d = "int[:]"
A2d = "int[:, :]"


@boost
def row_sum(arr: A2d, columns: A1d):
    return arr.T[columns].sum(0)


@boost(boundscheck=False, wraparound=False)
def row_sum_loops(arr: MV2d, columns: MV1d):
    # locals type annotations are used only for Cython
    i: int
    j: int
    sum_: int
    res: MV1d = np.empty(arr.shape[0], dtype=np.int64)
    for i in range(arr.shape[0]):
        sum_ = 0
        for j in range(columns.shape[0]):
            sum_ += arr[i, columns[j]]
        res[i] = sum_
    return res


if __name__ == "__main__":

    from util import check, bench

    functions = [row_sum, row_sum_loops]
    arr = np.arange(1_000_000).reshape(1_000, 1_000)
    columns = np.arange(1, 1000, 2)

    check(functions, arr, columns)
    bench(functions, arr, columns)
