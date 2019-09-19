import numpy as np

from transonic import jit, wait_for_all_extensions

import numba


def laplace_numpy(image):
    """Laplace operator in NumPy for 2D images."""
    laplacian = (
        image[:-2, 1:-1] + image[2:, 1:-1] + image[1:-1, :-2] + image[1:-1, 2:]
        - 4*image[1:-1, 1:-1]
    )
    thresh = np.abs(laplacian) > 0.05
    return thresh


def laplace_loops(image):
    """Laplace operator for 2D images."""
    h = image.shape[0]
    w = image.shape[1]
    laplacian = np.empty((h - 2, w - 2))
    for i in range(1, h - 1):
        for j in range(1, w - 1):
            laplacian[i-1, j-1] = (
                np.abs(image[i-1, j] + image[i+1, j] + image[i, j-1]
                + image[i, j+1] - 4*image[i, j]) > 0.05
            )
    return laplacian


laplace_transonic_pythran = jit(native=True, xsimd=True)(laplace_numpy)
laplace_transonic_python = jit(backend="python")(laplace_numpy)
laplace_transonic_numba = jit(backend="numba")(laplace_numpy)
laplace_numba = numba.jit(nopython=True, cache=True, fastmath=True)(laplace_numpy)

laplace_transonic_pythran_loops = jit(native=True, xsimd=True)(laplace_loops)
laplace_transonic_python_loops = jit(backend="python")(laplace_loops)
laplace_transonic_numba_loops = jit(backend="numba")(laplace_loops)
laplace_numba_loops = numba.jit(nopython=True, cache=True, fastmath=True)(
    laplace_loops
)

if __name__ == "__main__":
    from skimage.data import astronaut
    from skimage.color import rgb2gray

    image = astronaut()
    image = rgb2gray(image)

    laplace_transonic_python(image)

    laplace_transonic_pythran(image)
    laplace_transonic_pythran_loops(image)

    laplace_transonic_numba(image)
    laplace_transonic_numba_loops(image)

    laplace_numba(image)
    laplace_numba_loops(image)

    wait_for_all_extensions()

    # recall these functions to warm them
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
