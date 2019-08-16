# Cython backend

Cython code is much more complicated than Pythran code... We won't be able to
support all Cython features!

However, a descent set of Cython can be supported. We need to find Python
syntaxes for the most useful Cython special syntaxes.

Note that some Cython features are useless in Pythran (for example cdef of
locals variable, or `nogil`).

Note that ideally, we want to write Cython code that can be executed without
the Cython package and without Cython compilation. It is possible with a subset
of the "pure Python mode" of Cython for which the Python file does not depend
on Cython, i.e. all the supplementary information needed by Cython has to be
written in the .pxd file.

Therefore, we first need examples of Cython code written in this mode.


## Cython syntaxes already supported

### Simple fused types, memory views

We already have fused types in Transonic. With Transonic, we can already do (no
notion of C order):

```python
import numpy as np
from transonic import Transonic, Type, NDim, Array

np_floats = Type(np.float32, np.float64)
N = NDim(2, 3, 4)
A = Array[np_floats, N]
A1 = Array[np_floats, N + 1]
# or simply
A3d = Array[np_floats, "3d"]
```

### cdef for type declaration of local variables: `cython.locals`

In "pure Python mode", one can write

```cython
@cython.locals(result=np.float64_t, i=cython.int, n=cython.int)
cpdef mysum(np.float64_t[:] arr_input)
```

With variables annotations (which have to be removed for Pythran / Numba):

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

A nice Python syntax has to be found for `np_floats[:, :, ::1]`

It could just be

```python
A2 = Array[np_floats, "[:, :, ::1]"]
```

Note that for Pythran, we could also support:

```python
A_fixed_dim = Array[np_floats, "[:, :, 3]"]
```

### Cython decorators

```cython
@cython.boundscheck(False)
@cython.wraparound(False)
```

Unfortunately, it seems that we can't put these decorators in the .pxd file!

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
    ...
```

which would translate in Cython as something like:

```cython
cdef inline void func(np.float_t[:] a, cython.int n) nogil

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


## Cython syntaxes that will be difficult to support

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
