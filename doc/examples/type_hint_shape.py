"""
Not yet implemented...

Many things can be expressed in Pythran specifications (see
https://pythran.readthedocs.io/en/latest/MANUAL.html#concerning-pythran-specifications),
in particular stride arrays and partial shapes...

We could also express these concepts in strings, mainly following Pythran...

"""

from fluidpythran import pythran_def, TypeVar, NDimVar, ShapeVar, Array

T = TypeVar("T", int, float)

# here the shape of the array is only defined with the ShapeVar
A = Array[T, ShapeVar("S", "[3, :]", "[3, :, :]", "[::, ::]", "[::, ::, ::]")]


@pythran_def
def compute(a: A, b: A, c: T):
    return a + b

# if there is a NDimVar, we can use the ellipsis
A1 = Array[T, NDimVar("N", 1, 3), ShapeVar("S1", "[3, ...]", "[::, ...]")]


@pythran_def
def compute1(a: A1, b: A1, c: T):
    return c * (a + b)
