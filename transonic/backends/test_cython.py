from .cython import analyze_array_type


def test_float0():
    dtype, ndim = analyze_array_type("float[]")
    assert dtype == "np.float"
    assert ndim == 1


def test_float1():
    dtype, ndim = analyze_array_type("float[:]")
    assert dtype == "np.float"
    assert ndim == 1
