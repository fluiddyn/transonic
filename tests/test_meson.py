"""
TODO: we'd like to test the installation of the package data_tests/package_for_test_meson

The test is a bit complex because we need to

- create and activate a temporary virtual environment
- install transonic in editable mode
- install other build requirements (meson-python and ninja)
- make sure that there is not backend directories in package_for_test_meson (__pythran__, ...)
- install package_for_test_meson with `pip install . --no-build-isolation` (+ give the backend)
- test package_for_test_meson with `pytest tests`
- clean up the temporary virtual environment and package_for_test_meson directory

"""


def test_meson():
    ...
