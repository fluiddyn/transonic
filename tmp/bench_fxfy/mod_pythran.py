import numpy as np

# pythran export fxfy(float64[:], float64[:], float64[:])


def fxfy(ft, fn, theta):
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)
    fx = (cos_theta * ft) - (sin_theta * fn)
    fy = (sin_theta * ft) + (cos_theta * fn)
    return fx, fy


# pythran export fxfy_loops(float64[:], float64[:], float64[:])


def fxfy_loops(ft, fn, theta):
    n0 = theta.size
    fx = np.empty_like(ft)
    fy = np.empty_like(fn)
    for index in range(n0):
        sin_theta = np.sin(theta[index])
        cos_theta = np.cos(theta[index])
        fx[index] = (cos_theta * ft[index]) - (sin_theta * fn[index])
        fy[index] = (sin_theta * ft[index]) + (cos_theta * fn[index])
    return fx, fy
