from package_for_test_meson.bar import compute


def test_bar():
    assert compute() == 2
