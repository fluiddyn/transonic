(compile-at-import)=

# Install and configure

Transonic is a pure Python package and can be installed with

```sh
pip install transonic
```

In Conda environments, one can also use the equivalent commands with `conda` or
`mamba`.

Transonic is sensible to environment variables:

- `TRANSONIC_DIR` can be set to control where the cached files are
  saved.

- `TRANSONIC_DEBUG` triggers a verbose mode.

- `TRANSONIC_COMPILE_AT_IMPORT` can be set to enable a mode for which
  Transonic compiles at import time the Pythran file associated with the
  imported module. This behavior can also be triggered programmatically
  by using the function `set_compile_at_import`.

- `TRANSONIC_NO_REPLACE` can be set to disable all code replacements.
  This is useful to compare execution times and when measuring code coverage.

- `TRANSONIC_COMPILE_JIT` can be set to false to disable the
  compilation of jited functions. This can be useful for unittests.

- `TRANSONIC_BACKEND` to choose between the supported backends. The
  default backend "pythran" is quite robust. There are now 3 other backends:
  "cython", "numba" and "python" (prototypes).

- `TRANSONIC_MPI_TIMEOUT` sets the MPI timeout (default to 5 s).
