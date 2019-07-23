import os
from pathlib import Path
import runpy
import shutil
from contextlib import suppress

import pytest
from .path_data_tests import path_data_tests
from .mpi import nb_proc

from transonic.dist import make_backend_files

cwd = Path.cwd().absolute()
setup_dir = path_data_tests / "test_packaging"


def setup_module():
    os.chdir(setup_dir)
    transonic_src_paths = [setup_dir / "add.py"]
    make_backend_files(transonic_src_paths)


@pytest.mark.skipif(not path_data_tests.exists(), reason="no data tests")
@pytest.mark.skipif(nb_proc > 1, reason="No build_ext in MPI")
def test_buildext():
    os.chdir(setup_dir)
    runpy.run_path(str(setup_dir / "setup.py"))


def teardown_module():
    os.chdir(cwd)
    for namedir in ("build", "__pythran__", "__pycache__"):
        with suppress(FileNotFoundError):
            shutil.rmtree(setup_dir / namedir)

    to_remove = list(setup_dir.glob("*.h")) + list(setup_dir.glob("*.so"))
    for path in to_remove:
        os.remove(path)
