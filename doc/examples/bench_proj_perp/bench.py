
import numpy as np
from transonic import boost, Array, Type

A = Array[Type(np.float64, np.complex128), "3d"]
Af = "float[:,:,:]"
A = Af  # issue fused type with Cython


def proj(vx: A, vy: A, vz: A, kx: Af, ky: Af, kz: Af, inv_k_square_nozero: Af):
    tmp = (kx * vx + ky * vy + kz * vz) * inv_k_square_nozero
    vx -= kx * tmp
    vy -= ky * tmp
    vz -= kz * tmp


def proj_loop(vx: A, vy: A, vz: A, kx: Af, ky: Af, kz: Af, inv_k_square_nozero: Af):

    # type annotations only useful for Cython
    n0: int
    n1: int
    n2: int
    i0: int
    i1: int
    i2: int
    tmp: float

    n0, n1, n2 = kx.shape[0], kx.shape[1], kx.shape[2]

    for i0 in range(n0):
        for i1 in range(n1):
            for i2 in range(n2):
                tmp = (
                    kx[i0, i1, i2] * vx[i0, i1, i2]
                    + ky[i0, i1, i2] * vy[i0, i1, i2]
                    + kz[i0, i1, i2] * vz[i0, i1, i2]
                ) * inv_k_square_nozero[i0, i1, i2]

                vx[i0, i1, i2] -= kx[i0, i1, i2] * tmp
                vy[i0, i1, i2] -= ky[i0, i1, i2] * tmp
                vz[i0, i1, i2] -= kz[i0, i1, i2] * tmp


proj_pythran = boost(backend="pythran")(proj)
proj_numba = boost(backend="numba")(proj)
proj_cython = boost(backend="cython")(proj)

proj_loop_pythran = boost(backend="pythran")(proj_loop)
proj_loop_numba = boost(backend="numba")(proj_loop)
proj_loop_cython = boost(backend="cython", boundscheck=False, wraparound=False)(proj_loop)



if __name__ == "__main__":
    from textwrap import dedent

    import numba
    import pythran
    from transonic import __version__
    from transonic.util import timeit

    print(
        f"transonic {__version__}\n"
        f"pythran {pythran.__version__}\n"
        f"numba {numba.__version__}\n"
    )

    setup = dedent("""

        shape = n0, n1, n2 = 64, 512, 512
        k0 = np.linspace(0, 100, n0)
        k1 = np.linspace(0, 100, n1)
        k2 = np.linspace(0, 100, n2)
        K1, K0, K2 = np.meshgrid(k1, k0, k2, copy=False)
        kz = np.ascontiguousarray(K0)
        ky = np.ascontiguousarray(K1)
        kx = np.ascontiguousarray(K2)

        k_square_nozero = K0 ** 2 + K1 ** 2 + K2 ** 2
        k_square_nozero[0, 0, 0] = 1e-14
        inv_k_square_nozero = 1.0 / k_square_nozero

        vx = np.ones(shape)
        vy = np.ones(shape)
        vz = np.ones(shape)

    """)

    loc = locals()

    def bench(call, norm=None):
        ret = result = timeit(call, setup=setup, globals=loc)
        if norm is None:
            norm = result
        result /= norm
        print(f"{call.split('(')[0]:33s}: {result:.2f}")
        return ret


    norm = bench("proj(vx, vy, vz, kx, ky, kz, inv_k_square_nozero)")
    print(f"norm = {norm:.2e} s")

    for backend in ("cython", "numba", "pythran"):
        bench(f"proj_{backend}(vx, vy, vz, kx, ky, kz, inv_k_square_nozero)", norm=norm)
        bench(f"proj_loop_{backend}(vx, vy, vz, kx, ky, kz, inv_k_square_nozero)", norm=norm)