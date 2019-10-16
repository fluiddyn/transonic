import numpy as np

from transonic import boost, Array

A = Array[float, "3d"]
A1 = Array[float, "1d"]


def expr(a, b):
    return np.arctan2(2 * np.exp(a) ** 2 + 4 * np.log(a * b) ** 3, 2 / a)


def broadcast(a: A, b: A1, out: A):
    out[:] = expr(a, b)


def broadcast_loops(a: A, b: A1, out: A):
    n0, n1, n2 = a.shape
    for i0 in range(n0):
        for i1 in range(n1):
            for i2 in range(n2):
                out[i0, i1, i2] = expr(a[i0, i1, i2], b[i2])


broadcast_pythran = boost(backend="pythran")(broadcast)
broadcast_numba = boost(backend="numba")(broadcast)

broadcast_loops_pythran = boost(backend="pythran")(broadcast_loops)
broadcast_loops_numba = boost(backend="numba")(broadcast_loops)


if __name__ == "__main__":

    import numba
    import pythran
    from transonic import __version__
    from transonic.util import timeit

    shape = (4, 4, 64)
    a = np.linspace(1, 100, np.prod(shape)).reshape(shape)
    b = np.linspace(1, 100, shape[-1])
    out = np.empty_like(a)
    broadcast(a, b, out)
    out_loops = np.empty_like(a)
    broadcast_loops(a, b, out_loops)
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

    norm = bench("broadcast(a, b, out)")
    print(f"norm = {norm:.2e} s")

    for backend in ("numba", "pythran"):
        bench(f"broadcast_{backend}(a, b, out)", norm=norm)
        bench(f"broadcast_loops_{backend}(a, b, out)", norm=norm)
