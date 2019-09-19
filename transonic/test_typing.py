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
    Set,
    SetMeta,
    typeof,
    str2shape,
    MemLayout,
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
    assert str2type("int") == np.int
    assert str2type("float") == np.float
    assert str2type("uint32") == np.uint32


def test_str2type_arrays():
    A1 = Array[int, "1d"]
    compare_array_types(str2type("int[]"), A1)
    compare_array_types(str2type("int[:]"), A1)

    A2 = Array[np.uint32, "2d"]
    compare_array_types(str2type("uint32[:,:]"), A2)


def test_str2type_or():
    result = str2type("int or float")
    assert isinstance(result, UnionMeta)
    assert result.types == (int, float)

    result = str2type("int or float[]")
    assert isinstance(result, UnionMeta)
    compare_array_types(result.types[1], Array[float, "1d"])


def test_list():
    L = List[List[int]]
    repr(L)
    assert isinstance(L, ListMeta)
    assert L.format_as_backend_type(base_type_formatter) == "int list list"


def test_dict():
    D = Dict[str, int]
    repr(D)
    assert isinstance(D, DictMeta)
    assert D.format_as_backend_type(base_type_formatter) == "str: int dict"


def test_set():
    str2type("int set")
    S = Set["str"]
    S.get_template_parameters()
    repr(S)
    assert isinstance(S, SetMeta)
    assert S.format_as_backend_type(base_type_formatter) == "str set"


def test_tuple():
    T = str2type("(int, float[:, :])")
    T.get_template_parameters()
    assert repr(T) == 'Tuple[int, Array[float, "2d"]]'
    assert T.format_as_backend_type(base_type_formatter) == "(int, float64[:, :])"


def test_typeof_simple():
    assert typeof(1) is int
    assert typeof(1.0) is float
    assert typeof(1j) is complex
    assert typeof("foo") is str


def test_typeof_list():
    L = typeof([[1, 2], [3, 4]])
    assert isinstance(L, ListMeta)
    assert L.format_as_backend_type(base_type_formatter) == "int list list"


def test_typeof_dict():
    D = typeof({"a": 0, "b": 1})
    assert isinstance(D, DictMeta)
    assert D.format_as_backend_type(base_type_formatter) == "str: int dict"


def test_typeof_set():
    S = typeof({"a", "b"})
    assert isinstance(S, SetMeta)
    assert S.format_as_backend_type(base_type_formatter) == "str set"


def test_typeof_array():
    A = typeof(np.ones((2, 2)))
    compare_array_types(A, Array[np.float64, "2d"])


def test_typeof_np_scalar():
    T = typeof(np.ones(1)[0])
    assert T is np.float64


def test_shape():

    assert str2shape("[]") == (None,)
    assert str2shape("[:]") == (None,)
    assert str2shape("[][]") == (None,) * 2
    assert str2shape("[][ ]") == (None,) * 2

    assert str2shape("[:,:]") == (None,) * 2
    assert str2shape("[: ,:,:, ]") == (None,) * 3
    assert str2shape("[3 ,:,:]") == (3, None, None)
    assert str2shape("[ : , :,3]") == (None, None, 3)

    A = Array[int, "[: ,:, 3]"]
    assert A.shape == (None, None, 3)
    assert A.ndim.values[0] == 3
    assert repr(A) == 'Array[int, "[:,:,3]"]'

    assert (
        base_type_formatter.make_array_code(
            int, 2, (3, None), False, MemLayout.C_or_F
        )
        == "int[3, :]"
    )
