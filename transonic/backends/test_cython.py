import numpy as np

from transonic import Array, const
from transonic.backends import backends

backend = backends["cython"]
type_formatter = backend.type_formatter


def compare(result, dtype, ndim, memview, mem_layout=None, positive_indices=None):
    A = Array[dtype, ndim, memview, mem_layout, positive_indices]
    assert A.format_as_backend_type(type_formatter) == result


def test_memview():
    memview = "memview"
    compare("np.int_t[:, ::1]", int, "2d", memview, "C")
    compare("np.int_t[:, :, :]", int, "3d", memview, "strided")
    compare("np.int32_t[::1, :]", np.int32, "2d", memview, "F")


def test_array():
    memview = None
    compare('np.ndarray[np.int_t, ndim=2, mode="c"]', int, "2d", memview, "C")
    compare("np.ndarray[np.int_t, ndim=3]", int, "3d", memview, "strided")
    compare(
        'np.ndarray[np.int32_t, ndim=2, mode="f"]', np.int32, "2d", memview, "F"
    )
    compare(
        "np.ndarray[np.int_t, ndim=2, negative_indices=False]",
        int,
        "2d",
        memview,
        positive_indices="positive_indices",
    )


def test_const():
    A = Array[int, "2d"]
    assert "const " + A.format_as_backend_type(type_formatter) == const(
        A
    ).format_as_backend_type(type_formatter)
