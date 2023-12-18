from package_for_test_meson.foo import compute


def test_foo():
    assert compute() == 1
