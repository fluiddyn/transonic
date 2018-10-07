from .for_test_init import func, func1

from . import FluidPythran


def test_not_fluidpythranized():
    func(1, 3.14)
    func1(1.1, 2.2)


def test_use_pythran_false():
    FluidPythran(use_pythran=False)
