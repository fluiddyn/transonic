import os
import sys
from pathlib import Path
import runpy
import shutil
from contextlib import suppress

import pytest

from transonic.dist import make_backend_files
from transonic.mpi import nb_proc
from transonic.path_data_tests import path_data_tests
from transonic.config import backend_default

cwd = Path.cwd().absolute()
setup_dir = path_data_tests / "test_packaging"


def setup_module():
    os.chdir(setup_dir)
    transonic_src_paths = [setup_dir / "add.py"]
    make_backend_files(transonic_src_paths)


@pytest.fixture
def test_packaging():
    sys.path.append(str(path_data_tests))
    yield "test_packaging"
    sys.path.remove(str(path_data_tests))


@pytest.mark.skipif(backend_default != "pythran", reason="Speedup tests")
@pytest.mark.skipif(not path_data_tests.exists(), reason="no data tests")
@pytest.mark.skipif(nb_proc > 1, reason="No build_ext in MPI")
def test_buildext():
    os.chdir(setup_dir)
    runpy.run_path(str(setup_dir / "setup.py"))


def test_jit_mod_import(test_packaging):
    """JIT a function from an imported module"""
    runpy.run_module(f"{test_packaging}.base_mod_import")


def test_jit_func_import(test_packaging):
    """JIT an imported function"""
    runpy.run_module(f"{test_packaging}.base_func_import")


def teardown_module():
    os.chdir(cwd)
    for namedir in ("build", f"__{backend_default}__", "__pycache__"):
        with suppress(FileNotFoundError):
            shutil.rmtree(setup_dir / namedir)

    to_remove = list(setup_dir.glob("*.h")) + list(setup_dir.glob("*.so"))
    for path in to_remove:
        os.remove(path)
