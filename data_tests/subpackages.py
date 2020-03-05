from numpy.fft import rfft
from numpy.linalg import matrix_power
from numpy.random import randn

# TODO: requires test dependency scipy
# from scipy.special import jv

from transonic import boost


@boost
def test_np_fft(u: "float[]"):
    u_fft = rfft(u)
    return u_fft


@boost
def test_np_linalg_random(u: "float[:,:]"):
    nx, ny = u.shape
    u[:] = randn(nx, ny)
    u2 = u.T * u
    u4 = matrix_power(u2, 2)
    return u4


# @boost
# def test_sp_special(v:int, x:float):
#     return jv(v, x)
