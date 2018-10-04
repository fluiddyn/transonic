import sys
from shutil import rmtree

from . import path_data_tests

from .run import run


def test_create_pythran_files():
    path_dir_out = path_data_tests / "_pythran"
    if path_dir_out.exists():
        rmtree(path_dir_out)

    sys.argv = f"fluidpythran {path_data_tests / '*.py'}".split()
    run()

    sys.argv = f"fluidpythran {path_data_tests}".split()
    run()

    paths = path_data_tests.glob("*.py")
    sys.argv = ["fluidpythran"] + [str(path) for path in paths]
    run()

    path_file = path_data_tests / "classic.py"
    sys.argv = f"fluidpythran -v {path_file}".split()
    run()

    path_file.touch()
    run()

    path_file = path_data_tests / "_pythran/_pythran_classic.py"
    path_file.unlink()
    run()

    sys.argv = f"fluidpythran {path_file}".split()
    run()
