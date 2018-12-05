import sys

import time

import pytest

from . import path_data_tests
from .run import run
from . import util
from .compat import rmtree
from .mpi import nb_proc

path_dir_out = path_data_tests / "__pythran__"


@pytest.mark.skipif(nb_proc > 1, reason="No commandline in MPI")
def test_create_pythran_files():
    if path_dir_out.exists():
        rmtree(path_dir_out)

    sys.argv = f"fluidpythran -np {path_data_tests / '*.py'}".split()
    run()

    sys.argv = f"fluidpythran -np {path_data_tests}".split()
    run()

    paths = path_data_tests.glob("*.py")
    sys.argv = ["fluidpythran", "-np"] + [str(path) for path in paths]
    run()


@pytest.mark.skipif(nb_proc > 1, reason="No commandline in MPI")
def test_create_pythran_simple():

    sys.argv = "fluidpythran --version".split()
    run()

    sys.argv = ["fluidpythran"]
    run()


@pytest.mark.skipif(nb_proc > 1, reason="No commandline in MPI")
def test_create_pythran_classic():

    util.input = lambda: "y"

    if path_dir_out.exists():
        rmtree(path_dir_out)

    path_file = path_data_tests / "classic.py"
    sys.argv = f"fluidpythran -np -v {path_file}".split()
    run()

    print("after first build")
    run()

    time.sleep(0.02)
    path_file.touch()
    print("after touch")

    run()

    path_file_pythran = path_data_tests / "__pythran__/classic.py"
    path_file_pythran.unlink()

    print("after unlink")
    run()

    sys.argv = f"fluidpythran -cc {path_file}".split()
    run()

    sys.argv = f"fluidpythran {path_file}".split()
    run()

    sys.argv = f"fluidpythran -np {path_file_pythran}".split()
    run()
