# package_for_test_meson

We want to test that this works (for the different backends):

```sh
rm -rf src/package_for_test_meson/__pythran__/
pip install meson-python ninja
pip install . --no-build-isolation -vv
pytest tests
```

Since we cannot use a relative path in build-system.requires, we need to
manually install the build dependencies and install with `--no-build-isolation`.

We can also do something simple:

```
cd src/package_for_test_meson/
rm -rf __pythran__
transonic --meson bar.py foo.py
```
