# TODO: I guess the languages depend on the backend
# for example no cpp for backend "python"

# TODO: build dependencies (Cython, Pythran, ...) depend on the backend

project('package_for_test_meson', 'cpp')

py = import('python').find_installation(pure: false)


# taken from Scipy (TODO: adapt)

# This uses the path as is, and avoids running the interpreter.
incdir_numpy = meson.get_external_property('numpy-include-dir', 'not-given')
if incdir_numpy == 'not-given'
  incdir_numpy = run_command(py,
    [
      '-c',
      '''import numpy as np
incdir = np.get_include()
print(incdir)
  '''
    ],
    check: true
  ).stdout().strip()

else
  _incdir_numpy_abs = incdir_numpy
endif


inc_np = include_directories(incdir_numpy)
np_dep = declare_dependency(include_directories: inc_np)

backend = get_option('transonic-backend')

if backend == 'pythran'

  pythran = find_program('pythran', native: true)
  # xsimd is unvendored from pythran by conda-forge, and due to a compiler
  # activation bug the default <prefix>/include/ may not be visible (see
  # gh-15698). Hence look for xsimd explicitly.
  # xsimd_dep = dependency('xsimd', required: false)


  # This external-property may not be needed if we can use the native include
  # dir, see https://github.com/serge-sans-paille/pythran/issues/1394
  incdir_pythran = meson.get_external_property('pythran-include-dir', 'not-given')
  if incdir_pythran == 'not-given'
    incdir_pythran = run_command(py,
      [
        '-c',
      '''import pythran
incdir = pythran.get_include()
print(incdir)
'''
      ],
      check: true
    ).stdout().strip()
  endif
  pythran_dep = declare_dependency(
    include_directories: incdir_pythran,
    # dependencies: xsimd_dep,
  )

  cpp_args_pythran = [
    '-DENABLE_PYTHON_MODULE',
    '-D__PYTHRAN__=3',
    '-DPYTHRAN_BLAS_NONE'
  ]

else
  pythran_dep = []

endif

subdir('src/package_for_test_meson')
