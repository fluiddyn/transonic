def decor_1_value(value):
    return lambda x: x


cdivision = nonecheck = wraparound = boundscheck = decor_1_value


def nogil(func):
    return func
