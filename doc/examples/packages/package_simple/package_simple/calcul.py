import numpy as np

from transonic import Array, NDim, Type, boost

T = Type(np.int32, np.float64, np.float32)
A = Array[T, NDim(2)]


@boost
def laplace(image: A):
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
