from transonic import boost, Array
import numba

import numpy as np

Image = Array[np.float64, "2d", "C"]


def laplace_numpy(image: Image):
    """Laplace operator in NumPy for 2D images."""
    laplacian = (
        image[:-2, 1:-1]
        + image[2:, 1:-1]
        + image[1:-1, :-2]
        + image[1:-1, 2:]
        - 4 * image[1:-1, 1:-1]
    )
    thresh = np.abs(laplacian) > 0.05
    return thresh


def laplace_loops(image: Image):
    """Laplace operator for 2D images."""
    h = image.shape[0]
    w = image.shape[1]
    laplacian = np.empty((h - 2, w - 2), np.uint8)
    for i in range(1, h - 1):
        for j in range(1, w - 1):
            laplacian[i - 1, j - 1] = (
                np.abs(
                    image[i - 1, j]
                    + image[i + 1, j]
                    + image[i, j - 1]
                    + image[i, j + 1]
                    - 4 * image[i, j]
                )
                > 0.05
            )
    return laplacian


laplace_transonic_pythran = boost(backend="pythran")(laplace_numpy)
laplace_transonic_cython = boost(backend="cython")(laplace_numpy)
laplace_transonic_numba = boost(backend="numba")(laplace_numpy)
laplace_transonic_python = boost(backend="python")(laplace_numpy)
laplace_numba = numba.njit(laplace_numpy)


laplace_loops_transonic_pythran = boost(backend="pythran")(laplace_loops)
laplace_loops_transonic_python = boost(backend="python")(laplace_loops)
laplace_loops_transonic_numba = boost(backend="numba")(laplace_loops)
laplace_loops_numba = numba.njit(laplace_loops)


# For Cython, we need to add more type annotations

@boost(backend="cython", boundscheck=False, wraparound=False)
def laplace_loops_transonic_cython(image: Image):
    """Laplace operator for 2D images."""
    i: int
    j: int
    h: int = image.shape[0]
    w: int = image.shape[1]
    laplacian: Array[np.uint8, "2d"] = np.empty((h - 2, w - 2), np.uint8)
    for i in range(1, h - 1):
        for j in range(1, w - 1):
            laplacian[i - 1, j - 1] = (
                abs(
                    image[i - 1, j]
                    + image[i + 1, j]
                    + image[i, j - 1]
                    + image[i, j + 1]
                    - 4 * image[i, j]
                )
                > 0.05
            )
    return laplacian


if __name__ == "__main__":

    from skimage.data import astronaut
    from skimage.color import rgb2gray

    image = astronaut()
    image = rgb2gray(image)

    # call these functions to warm them
    laplace_transonic_numba(image)
    laplace_loops_transonic_numba(image)
    laplace_numba(image)
    laplace_loops_numba(image)

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
    bench("laplace_loops_transonic_pythran(image)", norm=norm)
    bench("laplace_transonic_cython(image)", norm=norm)
    bench("laplace_loops_transonic_cython(image)", norm=norm)
    bench("laplace_numba(image)", norm=norm)
    bench("laplace_transonic_numba(image)", norm=norm)
    bench("laplace_loops_numba(image)", norm=norm)
    bench("laplace_loops_transonic_numba(image)", norm=norm)
    bench("laplace_numpy(image)", norm=norm)
    bench("laplace_transonic_python(image)", norm=norm)
