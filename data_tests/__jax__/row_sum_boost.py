# __protected__ from jax import jit
import jax.numpy as np

# __protected__ @jit


def row_sum(arr, columns):
    return arr.T[columns].sum(0)


# __protected__ @jit


def row_sum_loops(arr, columns):
    # locals type annotations are used only for Cython
    # arr.dtype not supported for memoryview
    dtype = type(arr[0, 0])
    res = np.empty(arr.shape[0], dtype=dtype)
    for i in range(arr.shape[0]):
        sum_ = dtype(0)
        for j in range(columns.shape[0]):
            sum_ += arr[i, columns[j]]
        res[i] = sum_
    return res


__transonic__ = ("0.6.3+editable",)
