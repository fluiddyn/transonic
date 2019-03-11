from transonic import NDim


def test_annotation():
    N = NDim(1, 3)
    repr(N + 1)
    repr(N - 1)
