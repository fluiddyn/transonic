# About Cython with Transonic

Cython code is much more complicated than Pythran code... We won't be able to
support all Cython!

Let's try to describe a descent set of Cython that could be supported.

We need to find Python syntaxes for the most useful Cython special syntaxes!


## Cython syntaxes that can be supported quite easily

### ctypedef, fused types and contiguous arrays

```cython
cimport numpy as cnp
import numpy as np

ctypedef fused np_floats:
    cnp.float32_t
    cnp.float64_t

cdef np_floats[:, :, ::1] myvar

```

We already have fused types in Transonic. A nice Python syntax has to be found
for `np_floats[:, :, ::1]`

With Transonic, we can already do (no notion of C order):

```python
import numpy as np
from transonic import Transonic, Type, NDim, Array

np_floats = Type(np.float32, np.float64)
N = NDim(2, 3, 4)
A = Array[np_floats, N]
A1 = Array[np_floats, N + 1]

A2 = Array[np_floats, 3]
```

It could just be

```python
A2 = Array[np_floats, "[:, :, ::1]"]
```

Note that for Pythran, we could also support:

```python
A_fixed_dim = Array[np_floats, "[:, :, 3]"]
```

### Special C types

For example `Py_ssize_t`

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

### Function definition (cdef, cpdef, inline, nogil, return type)

```python
from transonic import boost

@boost(cython_options=["cdef", "inline", "nogil"])
def func(a: "float[]", n: int) -> "void":
    if n > 1:
        a[n-1] = 0
```

which would translate in Cython as something like:

```cython
cdef inline void func(float[] a, int n) nogil:
    if n > 1:
        a[n-1] = 0
```



### cdef for type declaration

In comments (the simplest solution):

```python
# cdef int myvar
myvar = 2

# cdef float a, b, c, d, e
```

Or with variables annotations (but they have to be removed for Pythran / Numba):

```python
myvar: int = 2
```

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


## Cython syntaxes that will be difficult (impossible) to support

### Pointers and addresses

```cython
cdef Py_ssize_t *p_indexer
```

### Definition `struc`, `enum`, `class`

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

### Cast

```cython
return <DTYPE_t*> myvar
```

### C allocation

```cython
features_carr = <MBLBP*>malloc(features_number * sizeof(MBLBP))
```
