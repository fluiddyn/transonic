# Release notes

% Unreleased_
% -----------

## [0.6.0] (unpublished)

- Support for [Meson build](https://transonic.readthedocs.io/en/latest/packaging.html)
  through `transonic --meson` and multi-backends
- Support for Python 3.12

## [0.5.3] (2023-08-21)

- [!110](https://foss.heptapod.net/fluiddyn/transonic/-/merge_requests/110)
  Quick fix autopep8 bug + fix CI (py3.9)

## [0.5.2] (2022-01-04)

- Better error if Pythran is not importable.

## [0.5.1] (2022-09-16)

- Fix 2 bugs (`runpath` with `pathlib.Path` and detection IPython)

## [0.5.0] (2022-02-04)

- New environment variable `TRANSONIC_MPI_TIMEOUT`
- Internal: faster import of modules using Transonic (using `sys._getframe`)
  ([!102](https://foss.heptapod.net/fluiddyn/transonic/-/merge_requests/102))

## [0.4.12] (2021-12-14)

- Fix [bug notebooks](https://foss.heptapod.net/fluiddyn/transonic/-/issues/45)

## 0.4.11 (2021-09-09)

- Fix bug Python 3.9 `ast._Unparser`

## 0.4.10 (2021-07-22)

- Towards Python 3.10 support by using Gast 0.5.0 and Beniget 0.4.0

## 0.4.9 (2021-07-02)

- Avoid new Gast and Beniget versions by pinning to the previous versions
  (0.4.0 and 0.3.0). No Python 3.10 support!

## 0.4.8 (2021-05-03)

- Python 3.9 support by using `ast._Unparser` instead of `astunparse`

## 0.4.7

- Numba backend: using by default `@njit(cache=True, fastmath=True)`
- Better logging with rich
- Support Pythran code using the omp module provided by Pythran

## 0.4.6

- Using [rich](https://pypi.org/project/rich) if available

## 0.4.5

- Quick fix incompatibility between pip/pep517 and colorlog

## 0.4.4

- Compatibility gast 0.4.0 (related to Python 3.9)

## 0.4.3 (2020-06-14)

- Various bugfixes

## 0.4.2 (2019-10-30)

- Improve usability (warnings, exceptions, API for benchmarks, ...)
- Python 3.8 support (with gast>=0.3.0 and beniget>=0.2.0)
- `const` function (for the C/Cython keyword)

## 0.4.1 (2019-10-08)

- Cython backend: less bugs, better support for fused types, nonecheck,
  cdivision, ...
- Fix default parameters for Pythran

## 0.4.0 (2019-09-22)

- An API to describe types (big refactoring)

  - memoryviews for Cython
  - memory layout for arrays (C, Fortran, C_or_F and strided)

- More than one backend in one process + API to select the backend for modules
  and functions

## 0.3.3 (2019-08-30)

- Keywords for the boost decorator: inline, boundscheck and wraparound

## 0.3.2 (2019-08-27)

- Improvements & bugfixes of Cython and Numba backends

## 0.3.1 (2019-08-23)

- Much better Cython backend
- Python and Numba backend

## 0.3.0 (2019-08-17)

(Pierre Blanc-fatin intership)

- Refactoring with backend classes
- Cython backend (alpha version)

## 0.2.4 (2019-06-28)

- Support source in multiple files ([#14](https://foss.heptapod.net/fluiddyn/transonic/issues/14) and #21)
- Fix issues #8 (Recursion for boosted method), #17 (Bad formating for Pythran
  error), #18 (Improve logging jit), #19 (Change default arguments of jit
  decorator) and #20 (No Pythran signature generated for boosted functions
  without arguments)!

## 0.2.3 (2019-06-11)

- The command transonic now blocks until the end of a AOT compilation
- Fix issue #13 (`jit(func)` and `boost(func)`, by Pierre Blanc-fatin)

## 0.2.2 (2019-06-05)

- Bugfix `and` and `or` (gast)!
- Fix issue #15 (selection code annotations, by Pierre Blanc-fatin)

## 0.2.1 (2019-04-11)

- Bugfixes: specifying gast version (>= 0.2.2) + path_data_tests

## 0.2.0 (2019-03-15)

- No need for {code}`include` and {code}`## transonic import ...`
- No import of the modules at compiled time (ast analyses with Beniget)!

## 0.1.13 (2019-03-06)

- Bugfixes for Windows

## 0.1.12 (2019-03-05)

- Depreciate `make_signature` (won't be available in 0.2.0)

## 0.1.11 (2019-02-12)

- Bugfix: @jit methods with ## transonic import.

## 0.1.10 (2019-02-07)

- Less verbose compilations (`pythran -v` obtained with `transonic -vv`)
- Bugfixes: Pythran "or" syntax for JIT and timeout with MPI

## 0.1.9.post0 (2019-01-30)

- Bugfix release with a more thoroughly tested {code}`ParallelBuildExt`.
- Pythonic `fspath`.

## 0.1.9 (2019-01-29)

- Common setup functions such as {code}`get_logger`,
  {code}`ParallelBuildExt` and {code}`init_pythran_extensions` in
  {code}`transonic.dist`.

## 0.1.8 (2019-01-19)

- Environment variable {code}`TRANSONIC_NO_REPLACE`

## 0.1.7 (2018-12-18)

- Bugfix: keep OMP comments!

## 0.1.6 (2018-12-14)

- Better logging and commandline (no compilation if the extension is
  up-to-date)

## 0.1.5 (2018-12-12)

- {code}`jit` for simple methods (without assignation to attributes
  and call of other methods)
- {code}`Union` for annotations
- {code}`include` decorator

## 0.1.4 (2018-12-06)

- {code}`boost` decorator for functions, simple methods (without assignation to
  attributes and call of other methods) and classes
- Bugfixes
- {code}`TRANSONIC_DIR`

## 0.1.3 (2018-12-04)

- Lock file during Pythran compilation
- {code}`__name__` and {code}`__doc__` preserved by decorators

## 0.1.2 (2018-12-03)

- Private command line {code}`_pythran-fluid` to call Pythran
- MPI aware (only process rank == 0 doing IO and compilation)
- Fix bug C-style `[][]`
- {code}`Array[float, "2d"]` supported
- {code}`NDim(0)` supported
- Function {code}`set_compile_jit()` to disable compilation of
  jit functions

## 0.1.1 (2018-11-28)

- {code}`wait_for_all_extensions`
- Bug fixes
- {code}`mocked_modules` argument for functions making AOT Pythran files

## 0.1.0 (2018-11-23)

- Compatibility PyPy3.5
- Fix bug script importing local script
- Command line option "clear-cache"

## 0.0.9 (2018-11-20)

- {code}`TRANSONIC_COMPILE_AT_IMPORT` mode for ahead-of-time and just-in-time
  compilation (works also in IPython)
- By default, the fluidpythran commandline uses Pythran

## 0.0.8 (2018-11-16)

- Fix jit when calling with new types
- {code}`jit` in IPython / Jupyter

## 0.0.7 (2018-11-15)

- {code}`jit` decorator (supports also type hints)

## 0.0.6 (2018-11-05)

- Type annotations to define Pythran functions and blocks

## 0.0.5 (2018-10-14)

- Add a dist package

[0.4.12]: https://foss.heptapod.net/fluiddyn/transonic/-/compare/0.4.11...0.4.12
[0.5.0]: https://foss.heptapod.net/fluiddyn/transonic/-/compare/0.4.12...0.5.0
[0.5.1]: https://foss.heptapod.net/fluiddyn/transonic/-/compare/0.5.0...0.5.1
[0.5.2]: https://foss.heptapod.net/fluiddyn/transonic/-/compare/0.5.1...0.5.2
[0.5.3]: https://foss.heptapod.net/fluiddyn/transonic/-/compare/0.5.2...0.5.3
[unreleased]: https://foss.heptapod.net/fluiddyn/transonic/-/compare/0.5.3...branch%2Fdefault
