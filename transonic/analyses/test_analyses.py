from transonic.analyses import get_types_from_transonic_signature


def assert_types_from_sig(signature, func_name, types):
    assert get_types_from_transonic_signature(signature, func_name) == types


def test_simple():
    assert_types_from_sig(
        "my_func(int, float64, )", "my_func", ["int", "float64"]
    )


def test_cython_style():
    assert_types_from_sig(
        "foo(int, int, int64[:, :], float64[:, :], float64[:, :], int64[:], int64[:, :, :], float64, float64, int, float64 )",
        "foo",
        [
            "int",
            "int",
            "int64[:, :]",
            "float64[:, :]",
            "float64[:, :]",
            "int64[:]",
            "int64[:, :, :]",
            "float64",
            "float64",
            "int",
            "float64",
        ],
    )


def test_c_style():
    assert_types_from_sig(
        "bar(int, int[] [] , int64[:, :], float64 )",
        "bar",
        ["int", "int[] []", "int64[:, :]", "float64"],
    )
