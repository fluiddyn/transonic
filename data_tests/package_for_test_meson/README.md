# package_for_test_meson

We want to test that this works (for the different backends):

```sh
pip install meson-python ninja
pip install . --no-build-isolation -vv
pytest tests
```

Since we cannot use a relative path in build-system.requires, we need to
manually install the build dependencies and install with `--no-build-isolation`.
