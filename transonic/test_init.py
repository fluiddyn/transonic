import importlib
from shutil import rmtree

from transonic import Transonic, mpi
from transonic.compiler import wait_for_all_extensions
from transonic.config import backend_default
from transonic.mpi import Path


def test_not_transonified():

    path_for_test = (
        Path(__file__).parent.parent / "_transonic_testing/for_test_init.py"
    )
    path_output = path_for_test.parent / f"__{backend_default}__"

    if path_output.exists() and mpi.rank == 0:
        rmtree(path_output)
    mpi.barrier()

    from _transonic_testing import for_test_init

    importlib.reload(for_test_init)

    from _transonic_testing.for_test_init import func, func1, check_class

    func(1, 3.14)
    func1(1.1, 2.2)
    check_class()


def test_use_pythran_false():
    Transonic(use_transonified=False)


def test_assign_boosted_func():
    from _transonic_testing.for_test_init import func0, func0_boosted

    func02 = func0(2, 6)
    result = func0_boosted(2, 6)
    wait_for_all_extensions()
    assert func02 == func0(2, 6)
    assert result == func0(2, 6)
