from numpy import pi

from transonic import boost

A = "float64[:]"


@boost
def unwrap_1d(image: A, unwrapped_image: A):
    """Phase unwrapping using the naive approach."""
    unwrapped_image[0] = image[0]
    periods = 0
    for i in range(1, image.shape[0]):
        difference = image[i] - image[i - 1]
        if difference > pi:
            periods -= 1
        elif difference < -pi:
            periods += 1
        unwrapped_image[i] = image[i] + 2 * pi * periods
