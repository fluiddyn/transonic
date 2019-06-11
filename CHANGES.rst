
Future
------

- Ability to use Cython and Numba (?)
- Alternative syntax for blocks (`issue #29
  <https://bitbucket.org/fluiddyn/fluidpythran/issues/29>`_)
- Source in multiple files (`issue #14
  <https://bitbucket.org/fluiddyn/fluidpythran/issues/14>`_)

0.2.3 (2019-06-11)
------------------

- The command transonic now blocks until the end of a AOT compilation
- Fix issue #13 (`jit(func)` and `boost(func)`, by Pierre Blanc-fatin)

0.2.2 (2019-06-05)
------------------

- Bugfix `and` and `or` (gast)!
- Fix issue #15 (selection code annotations, by Pierre Blanc-fatin)

0.2.1 (2019-04-11)
------------------

- Bugfixes: specifying gast version (>= 0.2.2) + path_data_tests

0.2.0 (2019-03-15)
------------------

- No need for :code:`include` and :code:`# transonic import ...`
- No import of the modules at compiled time (ast analyses with Beniget)!

0.1.13 (2019-03-06)
-------------------

- Bugfixes for Windows

0.1.12 (2019-03-05)
-------------------

- Depreciate `make_signature` (won't be available in 0.2.0)

0.1.11 (2019-02-12)
-------------------

- Bugfix: @jit methods with # transonic import.

0.1.10 (2019-02-07)
-------------------

- Less verbose compilations (`pythran -v` obtained with `transonic -vv`)
- Bugfixes: Pythran "or" syntax for JIT and timeout with MPI

0.1.9.post0 (2019-01-30)
------------------------

- Bugfix release with a more thoroughly tested :code:`ParallelBuildExt`.
- Pythonic `fspath`.

0.1.9 (2019-01-29)
------------------

- Common setup functions such as :code:`get_logger`,
  :code:`ParallelBuildExt` and :code:`init_pythran_extensions` in
  :code:`transonic.dist`.

0.1.8 (2019-01-19)
------------------

- Environment variable :code:`TRANSONIC_NO_REPLACE`

0.1.7 (2018-12-18)
------------------

- Bugfix: keep OMP comments!

0.1.6 (2018-12-14)
------------------

- Better logging and commandline (no compilation if the extension is
  up-to-date)

0.1.5 (2018-12-12)
------------------

- :code:`jit` for simple methods (without assignation to attributes
  and call of other methods)
- :code:`Union` for annotations
- :code:`include` decorator

0.1.4 (2018-12-06)
------------------

- :code:`boost` decorator for functions, simple methods (without assignation to
  attributes and call of other methods) and classes
- Bugfixes
- :code:`TRANSONIC_DIR`

0.1.3 (2018-12-04)
------------------

- Lock file during Pythran compilation
- :code:`__name__` and :code:`__doc__` preserved by decorators

0.1.2 (2018-12-03)
------------------

- Private command line :code:`_pythran-fluid` to call Pythran
- MPI aware (only process rank == 0 doing IO and compilation)
- Fix bug C-style `[][]`
- :code:`Array[float, "2d"]` supported
- :code:`NDim(0)` supported
- Function :code:`set_compile_jit()` to disable compilation of
  jit functions

0.1.1 (2018-11-28)
------------------

- :code:`wait_for_all_extensions`
- Bug fixes
- :code:`mocked_modules` argument for functions making AOT Pythran files

0.1.0 (2018-11-23)
------------------

- Compatibility PyPy3.5
- Fix bug script importing local script
- Command line option "clear-cache"

0.0.9 (2018-11-20)
------------------

- :code:`TRANSONIC_COMPILE_AT_IMPORT` mode for ahead-of-time and just-in-time
  compilation (works also in IPython)
- By default, the fluidpythran commandline uses Pythran

0.0.8 (2018-11-16)
------------------

- Fix jit when calling with new types
- :code:`jit` in IPython / Jupyter

0.0.7 (2018-11-15)
------------------

- :code:`jit` decorator (supports also type hints)

0.0.6 (2018-11-05)
------------------

- Type annotations to define Pythran functions and blocks

0.0.5 (2018-10-14)
------------------

- Add a dist package
