import sys
from shutil import rmtree

from . import path_data_tests

from .run import run

path_dir_out = path_data_tests / "__pythran__"


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


def test_create_pythran_classic():
    if path_dir_out.exists():
        rmtree(path_dir_out)

    path_file = path_data_tests / "classic.py"
    sys.argv = f"fluidpythran -v -np {path_file}".split()
    run()

    path_file.touch()
    run()

    path_file_pythran = path_data_tests / "__pythran__/_classic.py"
    path_file_pythran.unlink()
    run()

    sys.argv = f"fluidpythran {path_file}".split()
    run()
