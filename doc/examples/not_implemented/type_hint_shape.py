"""
Not yet implemented...

Many things can be expressed in Pythran specifications (see
https://pythran.readthedocs.io/en/latest/MANUAL.html#concerning-pythran-specifications),
in particular stride arrays and partial shapes...

We could also express these concepts in strings, mainly following Pythran...

"""

from transonic import boost, Type, NDim, Shape, Array

T = Type(int, float)

# here the shape of the array is only defined with the ShapeVar
A = Array[T, Shape("[3, :]", "[3, :, :]", "[::, ::]", "[::, ::, ::]")]


@boost
def compute(a: A, b: A, c: T):
    return a + b


# if there is a NDimVar, we can use the ellipsis
A1 = Array[T, NDim(1, 3), Shape("[3, ...]", "[::, ...]")]


@boost
def compute1(a: A1, b: A1, c: T):
    return c * (a + b)
