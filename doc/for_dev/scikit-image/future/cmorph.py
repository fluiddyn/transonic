import numpy as np

from transonic import boost, Optional, Array

A = Array[np.uint8, "2d", "memview"]


@boost(wraparound=False, boundscheck=False, cdivision=True, nonecheck=False)
def _dilate(
    image: A,
    selem: A,
    out: Optional[A] = None,
    shift_x: np.int8 = 0,
    shift_y: np.int8 = 0,
):
    """Return greyscale morphological dilation of an image.

    Morphological dilation sets a pixel at (i,j) to the maximum over all pixels
    in the neighborhood centered at (i,j). Dilation enlarges bright regions
    and shrinks dark regions.

    Parameters
    ----------

    image : ndarray
        Image array.
    selem : ndarray
        The neighborhood expressed as a 2-D array of 1's and 0's.
    out : ndarray
        The array to store the result of the morphology. If None, is
        passed, a new array will be allocated.
    shift_x, shift_y : bool
        shift structuring element about center point. This only affects
        eccentric structuring elements (i.e. selem with even numbered sides).

    Returns
    -------
    dilated : uint8 array
        The result of the morphological dilation.
    """

    rows: np.intp = image.shape[0]
    cols: np.intp = image.shape[1]
    srows: np.intp = selem.shape[0]
    scols: np.intp = selem.shape[1]

    centre_r: np.intp = int(selem.shape[0] / 2) - shift_y
    centre_c: np.intp = int(selem.shape[1] / 2) - shift_x

    image = np.ascontiguousarray(image)
    if out is None:
        out = np.zeros((rows, cols), dtype=np.uint8)

    selem_num: np.intp = np.sum(np.asarray(selem) != 0)
    sr: Array[np.intp, "1d", "memview"] = np.empty(selem_num, dtype=np.intp)
    sc: Array[np.intp, "1d", "memview"] = np.empty(selem_num, dtype=np.intp)

    s: np.intp = 0
    r: np.intp
    c: np.intp

    for r in range(srows):
        for c in range(scols):
            if selem[r, c] != 0:
                sr[s] = r - centre_r
                sc[s] = c - centre_c
                s += 1

    local_max: np.uint8
    value: np.uint8
    rr: np.intp
    cc: np.intp

    for r in range(rows):
        for c in range(cols):
            local_max = 0
            for s in range(selem_num):
                rr = r + sr[s]
                cc = c + sc[s]
                if 0 <= rr < rows and 0 <= cc < cols:
                    value = image[rr, cc]
                    if value > local_max:
                        local_max = value

            out[r, c] = local_max

    return np.asarray(out)


@boost
def _erode(
    image: A,
    selem: A,
    out: Optional[A] = None,
    shift_x: np.int8 = 0,
    shift_y: np.int8 = 0,
):
    """Return greyscale morphological erosion of an image.

    Morphological erosion sets a pixel at (i,j) to the minimum over all pixels
    in the neighborhood centered at (i,j). Erosion shrinks bright regions and
    enlarges dark regions.

    Parameters
    ----------
    image : ndarray
        Image array.
    selem : ndarray
        The neighborhood expressed as a 2-D array of 1's and 0's.
    out : ndarray
        The array to store the result of the morphology. If None is
        passed, a new array will be allocated.
    shift_x, shift_y : bool
        shift structuring element about center point. This only affects
        eccentric structuring elements (i.e. selem with even numbered sides).

    Returns
    -------
    eroded : uint8 array
        The result of the morphological erosion.
    """

    rows = image.shape[0]
    cols = image.shape[1]
    srows = selem.shape[0]
    scols = selem.shape[1]

    centre_r = int(selem.shape[0] / 2) - shift_y
    centre_c = int(selem.shape[1] / 2) - shift_x

    image = np.ascontiguousarray(image)
    if out is None:
        out = np.zeros((rows, cols), dtype=np.uint8)

    selem_num = np.sum(np.asarray(selem) != 0)
    sr = np.empty(selem_num, dtype=np.intp)
    sc = np.empty(selem_num, dtype=np.intp)

    s = 0
    for r in range(srows):
        for c in range(scols):
            if selem[r, c] != 0:
                sr[s] = r - centre_r
                sc[s] = c - centre_c
                s += 1

    for r in range(rows):
        for c in range(cols):
            local_min = 255
            for s in range(selem_num):
                rr = r + sr[s]
                cc = c + sc[s]
                if 0 <= rr < rows and 0 <= cc < cols:
                    value = image[rr, cc]
                    if value < local_min:
                        local_min = value

            out[r, c] = local_min

    return np.asarray(out)
