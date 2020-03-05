# __protected__ from numba import njit
from numpy.fft import rfft
from numpy.random import randn
from numpy.linalg import matrix_power

# __protected__ @njit


def test_np_fft(u):
    u_fft = rfft(u)
    return u_fft


# __protected__ @njit


def test_np_linalg_random(u):
    (nx, ny) = u.shape
    u[:] = randn(nx, ny)
    u2 = u.T * u
    u4 = matrix_power(u2, 2)
    return u4


__transonic__ = ("0.4.2",)
