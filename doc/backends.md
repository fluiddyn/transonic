# Supported backends

Transonic can use different tools to accelerate the code. We use the name
**backend**.

The default backend is Pythran and currently, there are 3 other backends
("cython", "numba" or "python"). The "python" backend is mainly used for
internal testing.

There are different methods to choose which backend is used:

- An environment variable {code}`TRANSONIC_BACKEND` (which has to be "pythran",
  "cython", "numba" or "python") should be used to change the backend globally
  for one process.
- The `transonic` command-line has an option `-b` (`--backend`).
- The functions {func}`transonic.backends.make_backend_files` and
  {func}`transonic.dist.init_transonic_extensions` have an optional argument
  `backend`. Note that these functions should be imported from the
  {mod}`transonic.dist` package.
- There are two functions {func}`transonic.config.set_backend` and
  {func}`transonic.backends.set_backend_for_this_module`. Note that these
  functions can be imported from the {mod}`transonic` package.
- The `boost` and `jit` decorators have an optional argument `backend`.

```{toctree}
:maxdepth: 2

examples/bench_row_sum/txt
backends/pythran
backends/cython
backends/numba
```
