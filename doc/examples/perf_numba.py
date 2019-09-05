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


@jit(native=True, xsimd=True)
def laplace_pythran(image):
    """Laplace operator in NumPy for 2D images."""
    laplacian = (
        image[:-2, 1:-1] + image[2:, 1:-1] + image[1:-1, :-2] + image[1:-1, 2:]
        - 4*image[1:-1, 1:-1]
    )
    thresh = np.abs(laplacian) > 0.05
    return thresh


@jit(native=True, xsimd=True)
def laplace_pythran_loops(image):
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


@numba.jit(nopython=True, cache=True, fastmath=True)
def laplace_numba(image):
    """Laplace operator in NumPy for 2D images. Numba accelerated."""
    laplacian = (
        image[:-2, 1:-1] + image[2:, 1:-1] + image[1:-1, :-2] + image[1:-1, 2:]
        - 4*image[1:-1, 1:-1]
    )
    thresh = np.abs(laplacian) > 0.05
    return thresh


@numba.jit(nopython=True, cache=True, fastmath=True)
def laplace_numba_loops(image):
    """Laplace operator for 2D images. Numba accelerated."""
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


if __name__ == "__main__":
    from skimage.data import astronaut
    from skimage.color import rgb2gray

    image = astronaut()
    image = rgb2gray(image)

    laplace_pythran(image)
    laplace_pythran_loops(image)

    laplace_numba(image)
    laplace_numba_loops(image)

    wait_for_all_extensions()

    from transonic.util import timeit
    from transonic import __version__
    import pythran

    loc = locals()

    def bench(call, norm=None):
        ret = result = timeit(call, globals=loc)
        if norm is None:
            norm = result
        result /= norm
        print(f"{call:30s}: {result:.2f}")
        return ret

    print(
        f"transonic {__version__}\n"
        f"pythran {pythran.__version__}\n"
        f"numba {numba.__version__}\n"
    )

    norm = bench("laplace_pythran(image)")
    bench("laplace_pythran_loops(image)", norm=norm)
    bench("laplace_numba(image)", norm=norm)
    bench("laplace_numba_loops(image)", norm=norm)
    bench("laplace_numpy(image)", norm=norm)
