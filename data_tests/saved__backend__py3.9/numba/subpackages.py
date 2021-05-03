# __protected__ from numba import njit
from numpy.fft import rfft
from numpy.random import randn
from numpy.linalg import matrix_power
from scipy.special import jv

# __protected__ @njit(cache=True, fastmath=True)


def test_np_fft(u):
    u_fft = rfft(u)
    return u_fft


# __protected__ @njit(cache=True, fastmath=True)


def test_np_linalg_random(u):
    (nx, ny) = u.shape
    u[:] = randn(nx, ny)
    u2 = u.T * u
    u4 = matrix_power(u2, 2)
    return u4


# __protected__ @njit(cache=True, fastmath=True)


def test_sp_special(v, x):
    return jv(v, x)


__transonic__ = ("0.4.7",)
