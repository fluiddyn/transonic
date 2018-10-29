from pathlib import Path
import importlib
import unittest

from .files_maker import make_pythran_file


class TestsInit(unittest.TestCase):

    path_for_test = Path(__file__).parent / "for_test_init.py"

    assert path_for_test.exists()

    path_output = path_for_test.parent / ("_pythran/_" + path_for_test.name)

    @classmethod
    def tearDownClass(cls):
        cls.path_output.unlink()

    def test_fluidpythranized(self):

        if self.path_output.exists():
            self.path_output.unlink()

        make_pythran_file(self.path_for_test)

        from . import for_test_init

        importlib.reload(for_test_init)

        assert self.path_output.exists()
        assert for_test_init.fp.is_pythranized

        for_test_init.func(1, 3.14)
        for_test_init.func1(1.1, 2.2)
