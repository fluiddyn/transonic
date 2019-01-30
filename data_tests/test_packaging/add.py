from transonic import boost

A = "int[]"


@boost
def add(f: A, g: A):
    return f + g
