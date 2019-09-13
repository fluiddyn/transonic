# Typing

With Transonic, we'd like to use clean and "pythonic" way to declare types. With recent versions of Python (>= 3.6), we can use type annotations.

Unfortunately, there is not yet a standard way to declare array types in
Python. Let's summarize how array types are declared in Pythran, Cython and
Numba.

## Pythran

Pythran users have to write signatures. The array types can be (see
<https://pythran.readthedocs.io/en/latest/MANUAL.html#concerning-pythran-specifications>)

```
# contiguous 1d array
int32[]
int32[:]

# stride 1d array
int32[::]

# contiguous 2d array
int32[][]
int32[:,:]

# stride 2d array
int32[::,::]

# contiguous C order 2d array
int32[:,:] order(C)

# contiguous Fortran order 2d array
int32[:,:] order(F)
```

## Cython

There are many ways to defined array types in Cython.

```python
# 1d np.ndarray
np.ndarray[np.int32_t, ndim=1]

# contiguous 2d np.ndarray (C order)
np.ndarray[np.float64_t, ndim=2, mode='c']

# indirect (pointer) data access
object[np.int32_t, ndim=1]

# 1d memoryview
np.int32_t[:]

# contiguous 1d memoryview
np.int32_t[::1]

# 2d memoryview
np.int32_t[:, :]

# contiguous 2d memoryview (C order)
np.int32_t[:, ::1]

# contiguous 2d memoryview (Fortran order)
np.int32_t[::1, :]
```

There are even more complicated notations with memoryviews:
<https://cython.readthedocs.io/en/latest/src/userguide/memoryviews.html#specifying-more-general-memory-layouts>

Memoryviews are more general (and in general more efficient) but there are
useful not supported features, for example broadcasting!

Not that fused types can be used to define data and array types:

```cython
ctypedef fused number:
    cython.int
    cython.float

# memoryview of number
number[:, ::1]

ctypedef fused array2d:
    cython.int[:, ::1]
    cython.float[:, ::1]
```

## Numba

See <https://numba.pydata.org/numba-doc/dev/reference/types.html>.

```python
import numba

# array from numba types
numba.int32[::1]

# same as
numba.types.Array(numba.int32, 1, "C")
```

It is also possible to pass signature(s) to the `jit` (or `njit`, or
`vectorize`) decorators (the order of the signatures is meaningful).

```python
@vectorize([int32(int32, int32),
            int64(int64, int64),
            float32(float32, float32),
            float64(float64, float64)])
def f(x, y):
    return x + y
```

## Transonic

To define multi-signatures from fused types, we can do:

```python
from transonic import Array, Type, NDim, boost

A = Array[Type(int, float), NDim(1, 2)]

@boost
def func(a: A, b: A):
    pass
```

Note that this other code should give a different result in term of signatures:

```python
from transonic import Array, Type, NDim, boost

A0 = Array[Type(int, float), NDim(1, 2)]
A1 = Array[Type(int, float), NDim(1, 2)]

@boost
def func(a: A0, b: A1):
    pass
```

## Issue about fused types

This works with Pythran and it should also work with other backends.

```python
from transonic import Type, boost

T = Type(int, float)

@boost
def func(n: int, d: T):
    tmp: T
    tmp = type(d)(0)
    _: int
    for _ in range(n):
        tmp += d
    return tmp


result = func(100, 1)
assert result == 100
assert isinstance(result, int)

result = func(100, 0.1)
assert np.allclose(result, 10.)
assert isinstance(result, float)
```

Same for this other case (useful for Cython):

```python
import numpy as np
from transonic import boost, Type, Array

A = Array[Type(np.float32, np.float64), "1d"]

@boost
def mysum(arr: A):

    result: A.dtype
    result = arr.dtype.type(0)
    i: np.int32

    for i in range(arr.shape[0]):
        result += arr[i]

    return result


data = np.ones(100, dtype=np.float32)
result = mysum(data)
assert np.allclose(result, 100.)
assert result.dtype == np.float32

data = np.ones(100)
result = mysum(data)
assert np.allclose(result, 100.)
assert isinstance(result, (float, np.float64))
# Pythran "bug" here!
assert result.dtype == np.float64
```
