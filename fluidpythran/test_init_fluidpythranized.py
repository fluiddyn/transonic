from pathlib import Path
import importlib
import unittest
import os
import time

try:
    import pythran
except ImportError:
    pythran = False


from .transpiler import make_pythran_file
from .util import has_to_pythranize_at_import, ext_suffix


class TestsInit(unittest.TestCase):

    path_for_test = Path(__file__).parent / "for_test_init.py"

    assert path_for_test.exists()

    path_pythran = path_for_test.parent / ("__pythran__/_" + path_for_test.name)
    path_ext = path_pythran.with_suffix(ext_suffix)

    @classmethod
    def tearDownClass(cls):
        # cls.path_pythran.unlink()
        if cls.path_ext.exists():
            cls.path_ext.unlink()

        try:
            os.environ.pop("PYTHRANIZE_AT_IMPORT")
        except KeyError:
            pass

    def __test_fluidpythranized(self):

        os.environ.pop("PYTHRANIZE_AT_IMPORT")

        assert not has_to_pythranize_at_import()

        if self.path_pythran.exists():
            self.path_pythran.unlink()

        make_pythran_file(self.path_for_test)

        from . import for_test_init

        importlib.reload(for_test_init)

        assert self.path_pythran.exists()
        assert for_test_init.fp.is_pythranized

        for_test_init.func(1, 3.14)
        for_test_init.func1(1.1, 2.2)

    @unittest.skipIf(not pythran, "Pythran is required for PYTHRANIZE_AT_IMPORT")
    def test_pythranize(self):

        os.environ["PYTHRANIZE_AT_IMPORT"] = "1"

        assert has_to_pythranize_at_import()

        if self.path_pythran.exists():
            self.path_pythran.unlink()

        make_pythran_file(self.path_for_test, log_level=None)

        assert self.path_pythran.exists()

        from . import for_test_init

        if not for_test_init.fp.is_compiling:
            importlib.reload(for_test_init)

        fp = for_test_init.fp

        assert fp.is_pythranized
        assert fp.is_compiling
        assert not fp.is_compiled

        for_test_init.func(1, 3.14)
        for_test_init.func1(1.1, 2.2)

        while not fp.is_compiled:
            time.sleep(0.1)
            for_test_init.func(1, 3.14)
            for_test_init.func1(1.1, 2.2)

        assert not fp.is_compiling
        assert fp.is_compiled

        for_test_init.func(1, 3.14)
        for_test_init.func1(1.1, 2.2)
