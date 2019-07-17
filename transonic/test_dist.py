import shutil
from distutils.core import Distribution
from copy import copy
import pytest

from . import dist
from .mpi import nb_proc

from .backends.pythran import PythranBackend
from .dist import (
    detect_pythran_extensions,
    modification_date,
    ParallelBuildExt,
    get_logger,
)
from .path_data_tests import path_data_tests


can_actually_import_pythran = copy(dist.can_import_pythran)


def setup_module():
    dist.can_import_pythran = True


@pytest.mark.skipif(not path_data_tests.exists(), reason="no data tests")
@pytest.mark.skipif(nb_proc > 1, reason="No dist in MPI")
def test_detect_pythran_extensions():

    shutil.rmtree(path_data_tests / "__pythran__", ignore_errors=True)

    names = [
        "block_fluidsim.py",
        "class_blocks.py",
        "no_pythran_.py",
        "type_hint_notemplate.py",
        "blocks_type_hints.py",
        "classic.py",
        "mixed_classic_type_hint.py",
        "assign_func_boost.py",
        "assign_func_jit.py",
        "boosted_func_use_import.py",
    ]

    pythranBE = PythranBackend()
    pythranBE.make_backend_files((path_data_tests / name for name in names))
    ext_names = detect_pythran_extensions(path_data_tests)
    # -2 files (no_pythran.py and assign_fun_jit.py) +2 files (__func__exterior_import_boost.py and __func__exterior_import_boost_2.py)
    assert len(ext_names) == len(names)

    shutil.rmtree(path_data_tests / "__pythran__", ignore_errors=True)


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
