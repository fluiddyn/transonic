
import importlib

from . import FluidPythran, mpi

from .compat import rmtree
from .mpi import Path


def test_not_fluidpythranized():

    path_for_test = Path(__file__).parent / "for_test_init.py"

    path_output = path_for_test.parent / "__pythran__"

    if path_output.exists() and mpi.rank == 0:
        rmtree(path_output)
    mpi.barrier()

    from . import for_test_init

    importlib.reload(for_test_init)

    from .for_test_init import func, func1

    func(1, 3.14)
    func1(1.1, 2.2)


def test_use_pythran_false():
    FluidPythran(use_pythran=False)
