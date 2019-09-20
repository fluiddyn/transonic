import numpy as np


def laplace_numpy(image):
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


def laplace_loops(image):
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
