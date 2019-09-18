import numpy as np

from transonic import Array

from .typing import base_type_formatter


def compare(dtype, ndim, mem_layout, result):
    A = Array[dtype, ndim, mem_layout]
    assert A.format_as_backend_type(base_type_formatter) == result


def test_array():
    compare(int, "2d", "C", "int[:, :] order(C)")
    compare(int, "3d", "strided", "int[::, ::, ::]")
    compare(np.int32, "2d", "F", "int32[:, :] order(F)")
