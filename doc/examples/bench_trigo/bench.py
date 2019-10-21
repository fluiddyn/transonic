import numpy as np

from transonic import boost, Array

A = Array[float, "1d"]


def fxfy(ft: A, fn: A, theta: A):
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)
    fx = cos_theta * ft - sin_theta * fn
    fy = sin_theta * ft + cos_theta * fn
    return fx, fy


def fxfy_loops(ft: A, fn: A, theta: A):
    n0 = theta.size
    fx = np.empty_like(ft)
    fy = np.empty_like(fn)
    for index in range(n0):
        sin_theta = np.sin(theta[index])
        cos_theta = np.cos(theta[index])
        fx[index] = cos_theta * ft[index] - sin_theta * fn[index]
        fy[index] = sin_theta * ft[index] + cos_theta * fn[index]
    return fx, fy


fxfy_pythran = boost(backend="pythran")(fxfy)
fxfy_numba = boost(backend="numba")(fxfy)

fxfy_loops_pythran = boost(backend="pythran")(fxfy_loops)
fxfy_loops_numba = boost(backend="numba")(fxfy_loops)


if __name__ == "__main__":

    from transonic.util import print_versions, timeit_verbose

    print_versions()

    theta = np.linspace(0, 2 * np.pi, 10000)
    ft = 2.5 * theta
    fv = 1.5 * theta
    loc = locals()

    out = fxfy(ft, fv, theta)
    out_loops = fxfy_loops(ft, fv, theta)
    assert np.allclose(out, out_loops)

    print()
    norm = timeit_verbose("fxfy(ft, fv, theta)", globals=loc)

    for backend in ("numba", "pythran"):
        timeit_verbose(f"fxfy_{backend}(ft, fv, theta)", globals=loc, norm=norm)
        timeit_verbose(
            f"fxfy_loops_{backend}(ft, fv, theta)", globals=loc, norm=norm
        )
