import numpy as np

from transonic.typing import (
    Array,
    NDim,
    str2type,
    UnionMeta,
    List,
    ListMeta,
    Dict,
    DictMeta,
    analyze_array_type,
)

from transonic.backends.typing import base_type_formatter


def compare_array_types(A0, A1):

    assert A0.dtype == A1.dtype

    if len(A0.ndim.values) > 1:
        raise NotImplementedError

    if len(A1.ndim.values) > 1:
        raise NotImplementedError

    assert A0.ndim.values[0] == A1.ndim.values[0]


def test_NDim():
    N = NDim(1, 3)
    repr(N + 1)
    repr(N - 1)


def test_str2type_simple():

    str2type("int") == np.int
    str2type("float") == np.float


def test_str2type_arrays():
    A1 = Array[int, "1d"]
    compare_array_types(str2type("int[]"), A1)
    compare_array_types(str2type("int[:]"), A1)

    A2 = Array[int, "2d"]
    compare_array_types(str2type("int[:,:]"), A2)


def test_str2type_or():
    result = str2type("int or float")
    assert isinstance(result, UnionMeta)
    assert result.types == (int, float)

    result = str2type("int or float[]")
    assert isinstance(result, UnionMeta)
    compare_array_types(result.types[1], Array[float, "1d"])


def test_list():
    L = List[List[int]]
    assert isinstance(L, ListMeta)
    assert L.format_as_backend_type(base_type_formatter) == "int list list"


def test_dict():
    D = Dict[str, int]
    assert isinstance(D, DictMeta)
    assert D.format_as_backend_type(base_type_formatter) == "str: int dict"


def test_float0():
    dtype, ndim = analyze_array_type("float[]")
    assert dtype == "np.float"
    assert ndim == 1


def test_float1():
    dtype, ndim = analyze_array_type("float[:]")
    assert dtype == "np.float"
    assert ndim == 1
