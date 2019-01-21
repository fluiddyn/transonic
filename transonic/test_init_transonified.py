import importlib
import unittest
import os
import time

try:
    import pythran
except ImportError:
    pythran = False


from .transpiler import make_pythran_file
from .util import (
    has_to_compile_at_import,
    ext_suffix,
    name_ext_from_path_backend,
)
from .aheadoftime import modules
from . import mpi

module_name = "transonic.for_test_init"


class TestsInit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path_for_test = mpi.Path(__file__).parent / "for_test_init.py"

        assert cls.path_for_test.exists()

        cls.path_pythran = path_pythran = (
            cls.path_for_test.parent / "__pythran__" / cls.path_for_test.name
        )
        cls.path_ext = path_pythran.with_name(
            name_ext_from_path_backend(path_pythran)
        )

    @classmethod
    def tearDownClass(cls):
        # cls.path_pythran.unlink()
        if cls.path_ext.exists():
            cls.path_ext.unlink()

        path_ext = cls.path_ext.with_suffix(ext_suffix)
        if path_ext.exists():
            path_ext.unlink()

        try:
            os.environ.pop("TRANSONIC_COMPILE_AT_IMPORT")
        except KeyError:
            pass

        print(mpi.rank, "end tearDownClass")

    def test_transonified(self):

        print(mpi.rank, "start test", flush=1)

        try:
            os.environ.pop("TRANSONIC_COMPILE_AT_IMPORT")
        except KeyError:
            pass

        try:
            del modules[module_name]
        except KeyError:
            pass

        assert not has_to_compile_at_import()

        print(mpi.rank, "before if self.path_pythran.exists()", flush=1)

        if self.path_pythran.exists():

            print(mpi.rank, "before self.path_pythran.unlink()", flush=1)

            self.path_pythran.unlink()

        print(mpi.rank, "before make_pythran_file(self.path_for_test)", flush=1)
        if mpi.rank == 0:
            make_pythran_file(self.path_for_test)

        print(mpi.rank, "after make_pythran_file(self.path_for_test)", flush=1)
        mpi.barrier()

        from . import for_test_init

        importlib.reload(for_test_init)

        assert self.path_pythran.exists()
        assert for_test_init.ts.is_transpiled

        for_test_init.func(1, 3.14)
        for_test_init.func1(1.1, 2.2)
        for_test_init.check_class()

    @unittest.skipIf(not pythran, "Pythran is required for TRANSONIC_COMPILE_AT_IMPORT")
    def test_pythranize(self):

        os.environ["TRANSONIC_COMPILE_AT_IMPORT"] = "1"

        try:
            del modules[module_name]
        except KeyError:
            pass

        assert has_to_compile_at_import()

        if self.path_pythran.exists():
            self.path_pythran.unlink()

        if self.path_ext.exists():
            self.path_ext.unlink()

        path_ext = self.path_ext.with_suffix(ext_suffix)
        if path_ext.exists():
            path_ext.unlink()

        from . import for_test_init

        if not for_test_init.ts.is_compiling:
            importlib.reload(for_test_init)

        assert module_name in modules, modules

        assert self.path_pythran.exists()

        ts = for_test_init.ts

        assert ts.is_transpiled
        assert ts.is_compiling
        assert not ts.is_compiled

        for_test_init.func(1, 3.14)
        for_test_init.func1(1.1, 2.2)

        while not ts.is_compiled:
            time.sleep(0.1)
            for_test_init.func(1, 3.14)
            for_test_init.func1(1.1, 2.2)

        assert not ts.is_compiling
        assert ts.is_compiled

        for_test_init.func(1, 3.14)
        for_test_init.func1(1.1, 2.2)
        for_test_init.check_class()
