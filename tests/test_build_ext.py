import os
import runpy
import shutil
import sys
from pathlib import Path

import pytest

from transonic.config import backend_default
from transonic.dist import make_backend_files
from transonic.mpi import nb_proc
from transonic.testing import path_data_tests

cwd = Path.cwd().absolute()


@pytest.fixture(scope="module")
def path_test_package(tmpdir_factory):
    path_input_dir = path_data_tests / "test_packaging"
    self = tmpdir_factory.mktemp("test_packaging")
    for path in path_input_dir.glob("*"):
        if path.suffix in {".c", ".py", ".pyx"}:
            shutil.copy(path, self)
    return self


@pytest.fixture(scope="module")
def path_prebuilt_package(path_test_package):
    os.chdir(path_test_package)
    transonic_src_paths = [path_test_package / "add.py"]
    make_backend_files(transonic_src_paths)
    return path_test_package


@pytest.fixture(scope="module")
def installed_package(path_prebuilt_package):
    sys.path.append(str(path_prebuilt_package))
    yield "test_packaging"
    sys.path.remove(str(path_prebuilt_package))


@pytest.mark.skipif(backend_default != "pythran", reason="Speedup tests")
@pytest.mark.skipif(not path_data_tests.exists(), reason="no data tests")
@pytest.mark.skipif(nb_proc > 1, reason="No build_ext in MPI")
def test_buildext(path_prebuilt_package):
    os.chdir(path_prebuilt_package)
    runpy.run_path(str(path_prebuilt_package / "setup.py"))


@pytest.mark.xfail(reason="Issue 23")
def test_jit_mod_import(installed_package):
    """JIT a function from an imported module"""
    runpy.run_module(f"{installed_package}.base_mod_import")


@pytest.mark.xfail(reason="Issue 23")
def test_jit_func_import(test_packaging):
    """JIT an imported function"""
    runpy.run_module(f"{test_packaging}.base_func_import")
