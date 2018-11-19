import sys
from shutil import rmtree
import time

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


def test_create_pythran_simple():

    sys.argv = "fluidpythran --version".split()
    run()

    sys.argv = ["fluidpythran"]
    run()


def test_create_pythran_classic():
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

    path_file_pythran = path_data_tests / "__pythran__/_classic.py"
    path_file_pythran.unlink()

    print("after unlink")
    run()

    sys.argv = f"fluidpythran {path_file}".split()
    run()

    sys.argv = f"fluidpythran -np {path_file_pythran}".split()
    run()
