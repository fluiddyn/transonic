import numpy as np

from transonic import Array
from transonic.backends import backends

backend = backends["cython"]
type_formatter = backend.type_formatter


def compare(dtype, ndim, memview, mem_layout, result):
    A = Array[dtype, ndim, memview, mem_layout]
    assert A.format_as_backend_type(type_formatter) == result


def test_memview():
    memview = "memview"
    compare(int, "2d", memview, "C", "np.int_t[:, ::1]")
    compare(int, "3d", memview, "strided", "np.int_t[:, :, :]")
    compare(np.int32, "2d", memview, "F", "np.int32_t[::1, :]")


def test_array():
    memview = None
    compare(int, "2d", memview, "C", 'np.ndarray[np.int_t, ndim=2, mode="c"]')
    compare(int, "3d", memview, "strided", "np.ndarray[np.int_t, ndim=3]")
    compare(
        np.int32, "2d", memview, "F", 'np.ndarray[np.int32_t, ndim=2, mode="f"]'
    )
