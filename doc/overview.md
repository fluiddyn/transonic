# Overview

## A short tour of Transonic public API

Transonic supports both ahead-of-time and just-in-time compilations. When using
the API for AOT compilation, the files need to be "[compiled](compiled)" to get speedup.

### Decorator `boost` and command `# transonic def`

```python
import h5py
import mpi4py

from transonic import boost

# transonic def myfunc(int, float)

@boost
def myfunc(a, b):
    return a * b

...
```

Most of this code looks familiar to Pythran users. The differences:

- One can use (for example) h5py and mpi4py (of course not in the Pythran
  functions).
- `# transonic def` instead of `# pythran export`.
- A tiny bit of Python... The decorator `@boost` replaces the
  Python function by the compiled function if Transonic has been used to
  produced the associated Pythran/Cython/Numba file.

### With type annotations

The previous example can be rewritten without `# transonic def`. It is
the recommended syntaxes for ahead-of-time compilation:

```python
import numpy as np
import h5py

from transonic import boost

@boost
def myfunc(a: float, d: int):
    return a * np.ones(d * [10])

...
```

Nice (shorter and clearer than with the Pythran command) but very limited (only
simple types and only one signature)... So one can also elegantly define many
signatures using Transonic types and/or Pythran types in strings (see [these
examples](https://transonic.readthedocs.io/en/latest/examples/type_hints.html) and our
API to define types (and fused types) in [transonic.typing](https://transonic.readthedocs.io/en/latest/generated/transonic.typing.html)).

Moreover, it is possible to add more signatures with `# transonic def`
commands.

### Targetting Cython

Cython needs to know the types of local variables to really speedup the
computations.  Transonic is able to write fast Cython from such code:

```python
from transonic import boost

@boost(boundscheck=False, wraparound=False)
def mysum(arr: "float[:]"):
    i: int
    n: int = arr.shape[0]
    result: float = 0.0
    for i in range(n):
        result += arr[i]
    return result
```

```{warning}
When targetting Cython, **don't use multi-signatures and prefer fused
types**. Cython itself does not support multi-signatures. Since these 2
mechanisms are so different, our Cython backend does not even try to
support multi-signatures. You'll get a warning if you use the Cython
backend with multi-signatures.
```

### Just-In-Time compilation

With Transonic, one can use the Ahead-Of-Time compilers Pythran and Cython in a
Just-In-Time mode. It is really the **easiest way to speedup a function with
Pythran**, just by adding a decorator! And it also works [in notebooks](https://transonic.readthedocs.io/en/latest/ipynb/executed/demo_jit.html)!

```python
import numpy as np

from transonic import jit

def func0(a, b):
    return a + b

@jit
def func1(a, b):
    return np.exp(a) * b * func0(a, b)
```

Note that the `@jit` decorator takes into account type hints (see
[the example in the documentation](https://transonic.readthedocs.io/en/latest/examples/using_jit.html)).

**Implementation details for just-in-time compilation:** A Pythran file is
produced for each "JITed" function (function decorated with `@jit`). The
file is compiled at the first call of the function and the compiled version is
used as soon as it is ready. The warmup can be quite long but the compiled
version is saved and can be reused (without warmup!) by another process.

### Define accelerated blocks

Transonic blocks can be used with classes and more generally in functions
with lines that cannot be compiled by Pythran.

```python
from transonic import Transonic

ts = Transonic()

class MyClass:

    ...

    def func(self, n):
        a, b = self.something_that_cannot_be_pythranized()

        if ts.is_transpiled:
            result = ts.use_block("name_block")
        else:
            # transonic block (
            #     float a, b;
            #     int n
            # )

            # transonic block (
            #     complex a, b;
            #     int n
            # )

            result = a**n + b**n

        return self.another_func_that_cannot_be_pythranized(result)
```

For blocks, we need a little bit more of Python.

- At import time, we have `ts = Transonic()`, which detects which
  Pythran module should be used and imports it. This is done at import time
  since we want to be very fast at run time.
- In the function, we define a block with three lines of Python and special
  Pythran annotations (`# transonic block`). The 3 lines of Python are used
  (i) at run time to choose between the two branches (`is_transpiled` or
  not) and (ii) at compile time to detect the blocks.

Note that the annotations in the command `# transonic block` are
different (and somehow easier to write) than in the standard command `#
pythran export`.

[Blocks can also be defined with type hints!](https://transonic.readthedocs.io/en/latest/examples/blocks.html)

```{warning}
I'm not satisfied by the syntax for blocks so I (PA) proposed an
alternative syntax in [issue #6](https://foss.heptapod.net/fluiddyn/transonic/issues/6).
```

### Python classes: `@boost` and `@jit` for methods

For simple methods **only using attributes**, we can write:

```python
import numpy as np

from transonic import boost

A = "float[:]"

@boost
class MyClass:

    arr0: A
    arr1: A

    def __init__(self, n):
        self.arr0 = np.zeros(n)
        self.arr1 = np.zeros(n)

    @boost
    def compute(self, alpha: float):
        return (self.arr0 + self.arr1).mean() ** alpha
```

```{warning}
Calling another method in a boosted method is not yet supported!
```

More examples on how to use Transonic for Object Oriented Programing are given
[here](https://transonic.readthedocs.io/en/latest/examples/methods.html).

(compiled)=

## Make the Pythran/Cython/Numba files and compile the extensions

### With `transonic` command

There is a command-line tool `transonic` which makes the associated
Pythran/Cython/Numba files from a Python file. For example one can run:

```bash
# Pythran is the default backend
transonic myfile.py -af "-march=native -DUSE_XSIMD -Ofast"
# Now using Cython
transonic myfile.py -b cython
```

By default and if the Python compiler is available, the produced files are
compiled.

### With the Meson Build system

Transonic is compatible with the [Meson Build system](https://mesonbuild.com/)
and there is a `--meson` option to be used in the `meson.build` files as shown
in the [example
packages](https://foss.heptapod.net/fluiddyn/transonic/-/tree/branch/default/data_tests/package_for_test_meson)
and in [Fluidsim](https://foss.heptapod.net/fluiddyn/fluidsim/)).

### With `setuptools`

There is also a function `make_backend_files` that can be used in a
`setup.py` like this:

```python
from pathlib import Path

from transonic.dist import make_backend_files

here = Path(__file__).parent.absolute()

paths = ["fluidsim/base/time_stepping/pseudo_spect.py"]
make_backend_files([here / path for path in paths])
```

Note that `make_backend_files` does not compile the backend files. The
compilation has to be done after the call of this function (see for example how
it is done in the [example packages](https://foss.heptapod.net/fluiddyn/transonic/src/default/doc/examples/packages/)).
