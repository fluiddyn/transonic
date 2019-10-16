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

    import numba
    import pythran
    from transonic import __version__
    from transonic.util import timeit

    theta = np.linspace(0, 2 * np.pi, 10000)
    ft = 2.5 * theta
    fv = 1.5 * theta
    out = fxfy(ft, fv, theta)
    out_loops = fxfy_loops(ft, fv, theta)
    assert np.allclose(out, out_loops)

    print(
        f"transonic {__version__}\n"
        f"pythran {pythran.__version__}\n"
        f"numba {numba.__version__}\n"
    )

    loc = locals()

    def bench(call, norm=None):
        ret = result = timeit(call, globals=loc)
        if norm is None:
            norm = result
        result /= norm
        print(f"{call.split('(')[0]:33s}: {result:.3f}")
        return ret

    norm = bench("fxfy(ft, fv, theta)")
    print(f"norm = {norm:.2e} s")

    for backend in ("numba", "pythran"):
        bench(f"fxfy_{backend}(ft, fv, theta)", norm=norm)
        bench(f"fxfy_loops_{backend}(ft, fv, theta)", norm=norm)
