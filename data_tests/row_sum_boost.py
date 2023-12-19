import numpy as np

from transonic import boost, Array

T_index = np.int32
# we use a type variable because it can be replaced by a fused type.
T = np.int64
A1d_i = Array[T_index, "1d"]
A1d = Array[T, "1d"]
A2d = Array[T, "2d"]
V1d_i = Array[T_index, "1d", "memview"]
V1d = Array[T, "1d", "memview"]
V2d = Array[T, "2d", "memview"]


@boost
def row_sum(arr: A2d, columns: A1d_i):
    return arr.T[columns].sum(0)


@boost(boundscheck=False, wraparound=False, cdivision=True, nonecheck=False)
def row_sum_loops(arr: V2d, columns: V1d_i):
    # locals type annotations are used only for Cython
    i: T_index
    j: T_index
    sum_: T
    # arr.dtype not supported for memoryview
    dtype = type(arr[0, 0])
    res: V1d = np.empty(arr.shape[0], dtype=dtype)
    for i in range(arr.shape[0]):
        sum_ = dtype(0)
        for j in range(columns.shape[0]):
            sum_ += arr[i, columns[j]]
        res[i] = sum_
    return res


if __name__ == "__main__":
    from util import check, bench

    functions = [row_sum, row_sum_loops]
    arr = np.arange(1_000_000).reshape(1_000, 1_000)
    columns = np.arange(1, 1000, 2, dtype=T_index)

    check(functions, arr, columns)
    bench(functions, arr, columns)
