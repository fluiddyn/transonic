from transonic import jit
import numba

from pure_numpy import laplace_numpy, laplace_loops

laplace_transonic_pythran = jit(native=True, xsimd=True)(laplace_numpy)
laplace_transonic_python = jit(backend="python")(laplace_numpy)
laplace_transonic_numba = jit(backend="numba")(laplace_numpy)
laplace_numba = numba.njit(laplace_numpy)

laplace_transonic_pythran_loops = jit(native=True, xsimd=True)(laplace_loops)
laplace_transonic_python_loops = jit(backend="python")(laplace_loops)
laplace_transonic_numba_loops = jit(backend="numba")(laplace_loops)
laplace_numba_loops = numba.njit(laplace_loops)

if __name__ == "__main__":
    from transonic import wait_for_all_extensions

    from skimage.data import astronaut
    from skimage.color import rgb2gray

    image = astronaut()
    image = rgb2gray(image)

    # warm the functions
    laplace_transonic_python(image)
    laplace_transonic_pythran(image)
    laplace_transonic_pythran_loops(image)
    laplace_transonic_numba(image)
    laplace_transonic_numba_loops(image)
    laplace_numba(image)
    laplace_numba_loops(image)

    wait_for_all_extensions()

    # again warming
    laplace_transonic_numba(image)
    laplace_transonic_numba_loops(image)

    from transonic.util import timeit
    from transonic import __version__
    import pythran

    loc = locals()

    def bench(call, norm=None):
        ret = result = timeit(call, globals=loc)
        if norm is None:
            norm = result
        result /= norm
        print(f"{call.split('(')[0]:33s}: {result:.2f}")
        return ret

    print(
        f"transonic {__version__}\n"
        f"pythran {pythran.__version__}\n"
        f"numba {numba.__version__}\n"
    )

    norm = bench("laplace_transonic_pythran(image)")
    print(f"norm = {norm:.2e} s")
    bench("laplace_transonic_pythran_loops(image)", norm=norm)
    bench("laplace_numba(image)", norm=norm)
    bench("laplace_transonic_numba(image)", norm=norm)
    bench("laplace_numba_loops(image)", norm=norm)
    bench("laplace_transonic_numba_loops(image)", norm=norm)
    bench("laplace_numpy(image)", norm=norm)
    bench("laplace_transonic_python(image)", norm=norm)
