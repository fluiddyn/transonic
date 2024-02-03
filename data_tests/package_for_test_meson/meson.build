# TODO: the languages should depend on the backend
# for example no cpp for backend "python"
# but the first statement should be this line...

project('package_for_test_meson', 'cpp')

# https://mesonbuild.com/Python-module.html
py_mod = import('python')
py = py_mod.find_installation('python3', pure: false)
py_dep = py.dependency()

backend = get_option('transonic-backend')

if backend.contains(',')
    backends = backend.split(',')
else
    backends = [backend]
endif

use_pythran = backend.contains('pythran')
if use_pythran
  incdir_numpy = run_command('transonic-get-include', 'numpy', check: true).stdout().strip()
  inc_np = include_directories(incdir_numpy)
  np_dep = declare_dependency(include_directories: inc_np)

  incdir_pythran = run_command('transonic-get-include', 'pythran', check: true).stdout().strip()
  pythran = find_program('pythran', native: true)

  cpp_args_pythran = [
    '-DENABLE_PYTHON_MODULE',
    '-D__PYTHRAN__=3',
    '-DPYTHRAN_BLAS_NONE'
  ]

  if get_option('use-xsimd') == true
    # xsimd is unvendored from pythran by conda-forge, and due to a compiler
    # activation bug the default <prefix>/include/ may not be visible (see
    # gh-15698). Hence look for xsimd explicitly.
    xsimd_dep = dependency('xsimd', required: false)
    pythran_dep = declare_dependency(
      include_directories: incdir_pythran,
      dependencies: xsimd_dep,
    )
    cpp_args_pythran += ['-DUSE_XSIMD']
  else
    pythran_dep = declare_dependency(
      include_directories: incdir_pythran,
    )
  endif

  pythran_complex_hook = get_option('pythran-complex-hook')
  if pythran_complex_hook == 'os-dependent'
    pythran_complex_hook = host_machine.system() == 'linux'
  endif

  if get_option('native')
    cpp_args_pythran += ['-march=native', '-Ofast']
  endif

endif

subdir('src/package_for_test_meson')
