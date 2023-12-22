import shutil
from setuptools import Distribution
from pprint import pformat

import pytest

from transonic.config import backend_default

from transonic.dist import (
    detect_transonic_extensions,
    modification_date,
    make_backend_files,
    ParallelBuildExt,
    get_logger,
)

from transonic.mpi import nb_proc
from transonic.path_data_tests import path_data_tests
from transonic.util import can_import_accelerator


@pytest.mark.skipif(not path_data_tests.exists(), reason="no data tests")
@pytest.mark.skipif(nb_proc > 1, reason="No dist in MPI")
def test_detect_backend_extensions():
    shutil.rmtree(path_data_tests / f"__{backend_default}__", ignore_errors=True)

    names = [
        "assign_func_boost.py",
        "assign_func_jit.py",
        "block_fluidsim.py",
        "blocks_type_hints.py",
        "boosted_func_use_import.py",
        # "boosted_class_use_import.py",  # was forgotten...
        "class_blocks.py",
        "classic.py",
        # "class_rec_calls.py",
        # "methods.py",
        "mixed_classic_type_hint.py",
        # "no_arg.py",
        "type_hint_notemplate.py",
        "no_pythran_.py",
    ]

    make_backend_files((path_data_tests / name for name in names))
    ext_names = detect_transonic_extensions(path_data_tests)

    if can_import_accelerator():
        ext_names = [
            name for name in ext_names if "package_for_test_meson" not in name
        ]

        # -2 files (no_pythran.py and assign_fun_jit.py)
        number_not_transonized = 2

        if len(ext_names) != len(names) - number_not_transonized:
            print("ext_names:\n", pformat(sorted(ext_names)), sep="")
            print("names:\n", pformat(sorted(names)), sep="")
            raise RuntimeError

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
