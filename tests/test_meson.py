"""Tests the Meson support

"""

import sys

from shutil import copy
from pathlib import Path
from unittest.mock import patch

import pytest

from transonic.run import run
from transonic.config import backend_default

test_dir = Path(__file__).absolute().parent

path_root_package_for_test_meson = (
    test_dir.parent / "data_tests/package_for_test_meson"
)

assert path_root_package_for_test_meson.exists()


def test_install_package():
    """
    TODO: we'd like to test the installation of the package data_tests/package_for_test_meson

    The test is a bit complex because we need to

    - create and activate a temporary virtual environment
    - install transonic in editable mode
    - install other build requirements (meson-python and ninja)
    - make sure that there is not backend directories in package_for_test_meson (__pythran__, ...)
    - install package_for_test_meson with `pip install . --no-build-isolation` (+ give the backend)
    - test package_for_test_meson with `pytest tests`
    - clean up the temporary virtual environment and package_for_test_meson directory

    """


@pytest.mark.xfail(backend_default == "cython", reason="Not yet implemented")
def test_meson_option(tmpdir, monkeypatch):
    """Only run `transonic --meson foo.py bar.py` in
    data_tests/package_for_test_meson/src/package_for_test_meson
    and compare with for_test__pythran__meson.build (same directory)
    """

    path_dir = path_root_package_for_test_meson / "src/package_for_test_meson"
    assert path_dir.exists()

    for name in ("foo.py", "bar.py", "meson.build"):
        copy(path_dir / name, tmpdir)

    monkeypatch.chdir(tmpdir)

    argv = "transonic --meson foo.py bar.py".split()
    with patch.object(sys, "argv", argv):
        run()

    path_result = tmpdir / f"__{backend_default}__/meson.build"
    assert path_result.exists()

    if backend_default == "numba":
        backend_default == "python"

    saved_output_path = path_dir / f"for_test__{backend_default}__meson.build"
    assert saved_output_path.exists()

    saved_meson_build = saved_output_path.read_text()
    produced_meson_build = path_result.read_text("utf8")

    assert saved_meson_build == produced_meson_build

    # TODO: check produced meson.build