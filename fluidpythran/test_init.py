from .for_test_init import func, func1


def test_not_fluidpythranized():
    func(1, 3.14)
    func1(1.1, 2.2)
