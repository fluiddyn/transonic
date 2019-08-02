import shutil
from distutils.core import Distribution
from copy import copy
import pytest

from . import dist
from .mpi import nb_proc

from .dist import (
    detect_transonic_extensions,
    modification_date,
    make_backend_files,
    ParallelBuildExt,
    get_logger,
)
from .path_data_tests import path_data_tests

from transonic.config import backend_default


can_actually_import_pythran = copy(dist.can_import_pythran)


def setup_module():
    dist.can_import_pythran = True


@pytest.mark.skipif(not path_data_tests.exists(), reason="no data tests")
@pytest.mark.skipif(nb_proc > 1, reason="No dist in MPI")
def test_detect_pythran_extensions():

    shutil.rmtree(path_data_tests / f"__{backend_default}__", ignore_errors=True)

    names = [
        "assign_func_boost.py",
        "assign_func_jit.py",
        "block_fluidsim.py",
        "blocks_type_hints.py",
        "boosted_func_use_import.py",
        "class_blocks.py",
        "classic.py",
        "mixed_classic_type_hint.py",
        "type_hint_notemplate.py",
        "no_pythran_.py",
    ]

    make_backend_files((path_data_tests / name for name in names))
    ext_names = detect_transonic_extensions(path_data_tests)
    if backend_default == "cython":
        # -2 files (no_pythran.py and assign_fun_jit.py) + 1 test_packaging.__cython__.add
        assert len(ext_names) == len(names) - 1
    else:
        # -2 files (no_pythran.py and assign_fun_jit.py)
        assert len(ext_names) == len(names) - 2
    shutil.rmtree(path_data_tests / f"__{backend_default}__", ignore_errors=True)


@pytest.mark.skipif(not path_data_tests.exists(), reason="no data tests")
@pytest.mark.skipif(nb_proc > 1, reason="No dist in MPI")
def test_modification_date():

    modification_date(path_data_tests / "no_pythran_.py")
    get_logger("bar")


@pytest.mark.skipif(not path_data_tests.exists(), reason="no data tests")
@pytest.mark.skipif(nb_proc > 1, reason="No dist in MPI")
def test_build_ext():
    dist = Distribution()
    build_ext = ParallelBuildExt(dist)

    build_ext.initialize_options()
    build_ext.parallel = 1
    build_ext.finalize_options()


def teardown_module():
    dist.can_import_pythran = can_actually_import_pythran
