# package_for_test_meson

We want to test that this works with transonic installed from source
(for the different backends):

```sh
rm -rf src/package_for_test_meson/__pyth*__/
pip install meson-python meson ninja
pip install . --no-build-isolation -vv
pytest tests
```

Since we cannot use a relative path in build-system.requires, we need to
manually install the build dependencies and install with `--no-build-isolation`.

We should also be able to install in editable mode with `pip install -e .
--no-build-isolation`. Note that with Meson, `--no-build-isolation` is always
needed for the editable mode (see
<https://meson-python.readthedocs.io/en/latest/how-to-guides/editable-installs.html>).

We can also do something simpler:

```
cd src/package_for_test_meson/
rm -rf __pythran__
transonic --meson bar.py foo.py
```
