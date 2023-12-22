import importlib
import unittest
import os
import time

from transonic.backends import backends
from transonic.config import backend_default
from transonic.util import (
    has_to_compile_at_import,
    ext_suffix,
    can_import_accelerator,
)
from transonic.aheadoftime import modules
from transonic import mpi

backend = backends[backend_default]

module_name = "_transonic_testing.for_test_init"


class TestsInit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path_for_test = (
            mpi.Path(__file__).parent
            / "../_transonic_testing/src/_transonic_testing/for_test_init.py"
        )

        assert cls.path_for_test.exists()

        cls.path_backend = path_backend = (
            cls.path_for_test.parent
            / f"__{backend_default}__"
            / cls.path_for_test.name
        )

        cls.path_ext = path_backend.with_name(
            backend.name_ext_from_path_backend(path_backend)
        )

    @classmethod
    def tearDownClass(cls):
        # cls.path_backend.unlink()
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

        print(mpi.rank, "before if self.path_backend.exists()", flush=1)

        if self.path_backend.exists():
            print(mpi.rank, "before self.path_backend.unlink()", flush=1)

            self.path_backend.unlink()

        print(mpi.rank, "before make_backend_file(self.path_for_test)", flush=1)
        if mpi.rank == 0:
            backend.make_backend_file(self.path_for_test)

        print(mpi.rank, "after make_backend_file(self.path_for_test)", flush=1)
        mpi.barrier()

        from _transonic_testing import for_test_init

        importlib.reload(for_test_init)

        assert self.path_backend.exists()
        assert for_test_init.ts.is_transpiled

        for_test_init.func(1, 3.14)
        for_test_init.func1(1.1, 2.2)
        for_test_init.check_class()

    @unittest.skipIf(
        not can_import_accelerator(),
        f"{backend.name} is required for TRANSONIC_COMPILE_AT_IMPORT",
    )
    def test_pythranize(self):
        os.environ["TRANSONIC_COMPILE_AT_IMPORT"] = "1"

        try:
            del modules[module_name]
        except KeyError:
            pass

        assert has_to_compile_at_import()

        if self.path_backend.exists():
            self.path_backend.unlink()

        if self.path_ext.exists():
            self.path_ext.unlink()

        path_ext = self.path_ext.with_suffix(ext_suffix)
        if path_ext.exists():
            path_ext.unlink()

        from _transonic_testing import for_test_init

        if not for_test_init.ts.is_compiling:
            importlib.reload(for_test_init)

        assert module_name in modules, modules
        assert self.path_backend.exists()

        ts = for_test_init.ts

        assert ts.is_transpiled
        if backend.needs_compilation:
            assert ts.is_compiling
            assert not ts.is_compiled
        else:
            assert ts.is_compiled

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
