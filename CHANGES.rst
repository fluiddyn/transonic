
Future
------

- :code:`pythran_def` for simple methods (without assignation to attributes
  and call of other methods)

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
- Function :code:`set_compile_cachedjit()` to disable compilation of
  cachedjit functions

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

- :code:`PYTHRANIZE_AT_IMPORT` mode for ahead-of-time and just-in-time
  compilation (works also in IPython)
- By default, the fluidpythran commandline uses Pythran

0.0.8 (2018-11-16)
------------------

- Fix cachedjit when calling with new types
- :code:`cachedjit` in IPython / Jupyter

0.0.7 (2018-11-15)
------------------

- :code:`cachedjit` decorator (supports also type hints)

0.0.6 (2018-11-05)
------------------

- Type annotations to define Pythran functions and blocks

0.0.5 (2018-10-14)
------------------

- Add a dist package
