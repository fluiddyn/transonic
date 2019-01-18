import numpy as np

# transonic import numpy as np

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


@jit
def laplace_pythran(image):
    """Laplace operator in NumPy for 2D images."""
    laplacian = (
        image[:-2, 1:-1] + image[2:, 1:-1] + image[1:-1, :-2] + image[1:-1, 2:]
        - 4*image[1:-1, 1:-1]
    )
    thresh = np.abs(laplacian) > 0.05
    return thresh


@jit
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


@numba.jit(nopython=True, cache=True)
def laplace_numba(image):
    """Laplace operator in NumPy for 2D images. Numba accelerated."""
    laplacian = (
        image[:-2, 1:-1] + image[2:, 1:-1] + image[1:-1, :-2] + image[1:-1, 2:]
        - 4*image[1:-1, 1:-1]
    )
    thresh = np.abs(laplacian) > 0.05
    return thresh


@numba.jit(nopython=True, cache=True)
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


"""
With
- clang 6.0
- pythran 0.9
- numba 0.40.1

%timeit laplace_numpy(image)
1.92 ms ± 69.7 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)

%timeit laplace_pythran(image)
211 µs ± 56.2 ns per loop (mean ± std. dev. of 7 runs, 1000 loops each)

%timeit laplace_pythran_loops(image)
241 µs ± 821 ns per loop (mean ± std. dev. of 7 runs, 1000 loops each)

%timeit laplace_numba(image)
2.05 ms ± 1.09 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)

%timeit laplace_numba_loops(image)
240 µs ± 489 ns per loop (mean ± std. dev. of 7 runs, 1000 loops each)

"""
