python_sources = [
  '__init__.py',
  'bar.py',
  'foo.py',
]

py.install_sources(
  python_sources,
  pure: false,
  subdir: 'package_for_test_meson',
)

backend = get_option('deps_backend')

# TODO: the new option --meson has to be implemented in transonic/run.py
run_command(['transonic', '--meson', '-b', backend, 'bar.py', 'foo.py'], check: true)

# subdir(f'__{backend}__')
