# Cython backend

Cython code is much more complicated than Pythran code... We won't be able to
support all Cython features!

However, a descent set of Cython can be supported. We need to find Python
syntaxes for the most useful Cython special syntaxes.

Note that some Cython features are useless in Pythran (for example cdef of
local variables, or `nogil`).

Note that ideally, we want to write Cython code that can be executed without
the Cython package and without Cython compilation. It is possible with the
["pure Python mode" of
Cython](https://cython.readthedocs.io/en/latest/src/tutorial/pure.html).
Therefore, we first need examples of Cython code written in this mode.

Note however, that this mode is currently still experimental and that we hit
simple Cython bugs which limit a lot what can be done in practice with the
Cython backend. For example:

- Pure-Python mode and fused types
  <https://github.com/cython/cython/issues/3142>
- `cython.locals(arr=np.ndarray[...])`
  <https://github.com/cython/cython/issues/3129>
- Incompatibility ccall/nogil in pure-Python mode:
  <https://github.com/cython/cython/issues/3169>
- nogil and pxd in pure-Python mode:
  <https://github.com/cython/cython/issues/3170>

More generally, there are many known bugs in Cython which do not help! For example:

- `ctypedef` and buffer
  <https://github.com/cython/cython/issues/754>
- Defining a fused type using a fused type
  <https://stackoverflow.com/questions/57887972>

I think at least some of these bugs have to be solved upstream...

## Cython syntaxes already supported

### `cpdef` signature with simple (basic and array) types for arguments

### `cdef` for type declaration of local variables: `cython.locals`

In "pure Python mode", one can write

```cython
@cython.locals(result=np.float64_t, i=cython.int, n=cython.int)
cpdef mysum(np.float64_t[:] arr_input)
```

With variables annotations (which are removed for Pythran / Numba):

```python
from transonic import boost

@boost
def mysum(arr_input: "float[]"):
    i: int
    n: int = arr_input.shape[0]
    result: float = 0.
    for i in range(n):
        result += arr_input[i]
    return result
```

### Cython decorators

```cython
@cython.boundscheck(False)
@cython.wraparound(False)
```

Currently only for simple functions (no methods).

## Cython syntaxes partly supported

### Function definition (cdef, cpdef, inline, nogil, return type)

```python
from transonic import boost

@boost(inline=True, nogil=True)
def func(a: "float[]", n: int) -> "void":
    ...
```

which would translate in Cython as something like:

```cython
cpdef inline void func(np.ndarray[np.float_t, ndim=1] a, cython.int n) nogil
```

- all function signatures use `cpdef` (?)

- `boost(inline=True)` is supported for functions, see [this
  example](https://transonic.readthedocs.io/en/latest/examples/inlined/txt.html).

- Return type is supported and there is a void type (`"void"` or `np.void`).

### Fused types

We already have fused types in Transonic. With Transonic, we can already do:

```python
import numpy as np
from transonic import Array, Type, NDim

np_floats = Type(np.float32, np.float64)
N = NDim(2, 3, 4)
A = Array[np_floats, N]
A1 = Array[np_floats, N + 1]
# or simply
A3d = Array[np_floats, "3d"]
```

However, Cython Fused types are currently very limited.

Even with something as simple as that

```python
from transonic import Array, Type

A = Array[Type(np.float64, np.complex128), "1d"]

def mysum(arr: A):
    result: A.dtype = arr.dtype.type(0.)
    i: int
    for i in range(arr.shape[0]):
        result += arr[i]
    return result
```

should be translated to this (not supported, see
<https://github.com/cython/cython/issues/754>) Cython code:

```cython
import cython

import numpy as np
cimport numpy as np

ctypedef fused T0:
   np.complex128_t
   np.float64_t

ctypedef np.ndarray[T0, ndim=1] A

def mysum(A arr):
    cdef T0 ret = arr.dtype.type(0.)
    cdef cython.int i
    for i in range(arr.shape[0]):
        ret += arr[i]
    return ret
```

Note that it works with a memoryview... (but not in pure-Python mode!)

Note that another working alternative is:

```
import cython

import numpy as np
cimport numpy as np

ctypedef fused T0:
   np.complex128_t
   np.float64_t

def mysum(np.ndarray[T0, ndim=1] arr):
    cdef T0 ret = arr.dtype.type(0.)
    cdef cython.int i
    for i in range(arr.shape[0]):
        ret += arr[i]
    return ret
```

But the corresponding pure-Python version does not work!

### More array types (contiguous arrays, C or F order, memoryviews)

I think we should support:

```python
Array[int, NDim(3), "C"]
Array[int, "3d", "C"]
transonic.typeof(np.empty((2, 2, 2)))

Array["int[:, :, ::1]"]
Array[int, "[:, :, ::1]"]
transonic.str2type("int[:, :, ::1]")
```

and maybe also:

```python
transonic.int64[:, :, ::1]
```

I tend to think that the default (`"int[:,:]"`) should correspond to
`"order=C"`. "Fortran" order and "any" order (contiguous C or F) could be
obtained with `"order=F"` and `"order=any"`.

Strided arrays could be obtained with `Array[int, NDim(3), "strided"]` or
`str2type("int[::, ::, ::]")`.

Note that for Pythran, we could also support:

```python
A_fixed_dim = Array[Type(np.float32, float), "[:, :, 3]"]
```

For Cython, we need to be able to specify if an array is a `np.ndarray` or a
`memoryview`. By default, we will use `np.ndarray` and `memoryview` could be
obtained with:

```python
Array[int, "[:, :, ::1]", "memview"]
```

### Special C types

For example `Py_ssize_t` (nearly `np.intp`, which is supported) and `void` (supported)

```python
from ctypes import c_ssize_t as Py_ssize_t
from transonic import boost

@boost
def func(arr: "float[]", index: Py_ssize_t):
    if n > 1:
        a[n-1] = 0

```

or just:

```python
from transonic import boost

@boost
def func(arr: "float[]", index: "Py_ssize_t"):
    ...

```

## Cython syntaxes that can be supported quite easily

### `with nogil:`

We could support something like

```python
from transonic import boost, nogil

@boost
def func(n: int):

    with nogil:
        result = n**2

    return result

```

Of course there is no equivalent in Pythran, so the Pythran backend would have
to suppress the `with nogil()`.

### Cast

```cython
return <DTYPE_t*> myvar
```

I guess we should follow Cython and its pure Python mode function
`cython.cast(type, myvar)`.

## Cython syntaxes that will be difficult to support

### Pointers and addresses

```cython
cdef Py_ssize_t *p_indexer
```

### Definition `struct`, `enum`, `class`

```cython
cdef struct Heap:
    Py_ssize_t items
    Py_ssize_t space
    Heapitem *data
    Heapitem **ptrs
```

or

```cython
cdef class Foo:
```

### C allocation

```cython
features_carr = <MBLBP*>malloc(features_number * sizeof(MBLBP))
```
