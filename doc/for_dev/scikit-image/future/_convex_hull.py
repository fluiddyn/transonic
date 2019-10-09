import numpy as np

from transonic import boost, Array


@boost(wraparound=False, boundscheck=False, cdivision=True, nonecheck=False)
def possible_hull(img: "uint8[:,:]"):
    """Return positions of pixels that possibly belong to the convex hull.

    Parameters
    ----------
    img : ndarray of bool
        Binary input image.

    Returns
    -------
    coords : ndarray (cols, 2)
       The ``(row, column)`` coordinates of all pixels that possibly belong to
       the convex hull.

    """
    r: np.intp
    c: np.intp
    rows: np.intp = img.shape[0]
    cols: np.intp = img.shape[1]

    # Output: rows storage slots for left boundary pixels
    #         cols storage slots for top boundary pixels
    #         rows storage slots for right boundary pixels
    #         cols storage slots for bottom boundary pixels
    coords = np.ones((2 * (rows + cols), 2), dtype=np.intp)
    coords *= -1

    nonzero: Array[np.intp, "2d", "C", "memview"] = coords

    rows_cols: np.intp = rows + cols
    rows_2_cols: np.intp = 2 * rows + cols

    for r in range(rows):

        rows_cols_r = rows_cols + r

        for c in range(cols):

            if img[r, c] != 0:

                rows_c = rows + c
                rows_2_cols_c = rows_2_cols + c

                # Left check
                if nonzero[r, 1] == -1:
                    nonzero[r, 0] = r
                    nonzero[r, 1] = c

                # Right check
                elif nonzero[rows_cols_r, 1] < c:
                    nonzero[rows_cols_r, 0] = r
                    nonzero[rows_cols_r, 1] = c

                # Top check
                if nonzero[rows_c, 1] == -1:
                    nonzero[rows_c, 0] = r
                    nonzero[rows_c, 1] = c

                # Bottom check
                elif nonzero[rows_2_cols_c, 0] < r:
                    nonzero[rows_2_cols_c, 0] = r
                    nonzero[rows_2_cols_c, 1] = c

    return coords[coords[:, 0] != -1]
