from pathlib import Path
import shutil
import importlib

from . import FluidPythran


def test_not_fluidpythranized():

    path_for_test = Path(__file__).parent / "for_test_init.py"

    path_output = path_for_test.parent / "_pythran"

    if path_output.exists():
        shutil.rmtree(path_output)

    from . import for_test_init

    importlib.reload(for_test_init)

    from .for_test_init import func, func1

    func(1, 3.14)
    func1(1.1, 2.2)


def test_use_pythran_false():
    FluidPythran(use_pythran=False)
