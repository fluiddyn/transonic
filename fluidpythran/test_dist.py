
import shutil

import pytest

from . import dist
from .mpi import nb_proc

from .dist import detect_pythran_extensions, modification_date, make_pythran_files
from . import path_data_tests

dist.can_import_pythran = True

shutil.rmtree(path_data_tests / "__pythran__", ignore_errors=True)


@pytest.mark.skipif(nb_proc > 1, reason="No dist in MPI")
def test_detect_pythran_extensions():

    names = [
        "block_fluidsim.py",
        "class_blocks.py",
        "no_pythran_.py",
        "type_hint_notemplate.py",
        "blocks_type_hints.py",
        "classic.py",
        "mixed_classic_type_hint.py",
        "type_hint.py",
    ]

    make_pythran_files(
        (path_data_tests / name for name in names),
        mocked_modules=("toto.titi", "numpy"),
    )
    ext_names = detect_pythran_extensions(path_data_tests)
    assert len(ext_names) == len(names) - 1


@pytest.mark.skipif(nb_proc > 1, reason="No dist in MPI")
def test_modification_date():

    modification_date(path_data_tests / "no_pythran_.py")
