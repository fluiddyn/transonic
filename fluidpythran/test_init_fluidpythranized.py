from pathlib import Path
import importlib
import unittest

from .files_maker import create_pythran_file

path_for_test = Path(__file__).parent / "for_test_init.py"

assert path_for_test.exists()

print(path_for_test)

path_output = path_for_test.parent / ("_pythran/_pythran_" + path_for_test.name)

if path_output.exists():
    path_output.unlink()

create_pythran_file(path_for_test)

print("path_output", path_output)

from . import for_test_init

importlib.reload(for_test_init)


class TestsInit(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        path_output.unlink()

    def test_fluidpythranized(self):

        assert path_output.exists()
        assert for_test_init.fp.is_pythranized

        for_test_init.func(1, 3.14)
        for_test_init.func1(1.1, 2.2)
