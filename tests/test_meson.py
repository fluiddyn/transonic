"""Tests the Meson support

"""

import sys
import subprocess
import os

from shutil import copy
from pathlib import Path
from unittest.mock import patch

import pytest

from transonic.run import run
from transonic.config import backend_default
from transonic.mpi import nb_proc

test_dir = Path(__file__).absolute().parent

path_root_package = test_dir.parent / "data_tests/package_for_test_meson"
assert path_root_package.exists()

path_src_package = path_root_package / "src/package_for_test_meson"
assert path_src_package.exists()


def run_in_venv(venv, command, cwd=None):
    try:
        env = venv.env
    except AttributeError:
        path_bin = Path(venv.path) / "bin"
        env = os.environ.copy()
        env["PATH"] = str(path_bin) + ":" + os.environ["PATH"]
        venv.env = env

    args = [venv.python, "-m"]
    args.extend(command.split())
    subprocess.run(args, cwd=cwd, check=True, env=env)


@pytest.mark.skipif(nb_proc > 1, reason="No commandline in MPI")
@pytest.mark.xfail(
    backend_default not in ["pythran", "python"], reason="Not yet implemented"
)
def test_install_package(tmpdir, venv):
    """
    Test the installation of the package data_tests/package_for_test_meson

    - create and activate a temporary virtual environment
    - create a clean package_for_test_meson in tmp directory
    - install transonic from source
    - install other build requirements (meson-python and ninja) and pytest
    - install pythran for the pythran backend
    - install package_for_test_meson with `pip install . --no-build-isolation` (+ give the backend)
    - test package_for_test_meson with `pytest tests`

    """

    assert venv.python.endswith("/bin/python")

    for name in ("pyproject.toml", "meson.build", "meson.options", "README.md"):
        copy(path_root_package / name, tmpdir)

    src_dir = path_root_package / "tests"
    dst_dir = tmpdir / "tests"
    dst_dir.mkdir()
    for name in ("test_bar.py", "test_foo.py"):
        copy(src_dir / name, dst_dir)

    src_dir = path_src_package
    dst_dir = Path(tmpdir / "src/package_for_test_meson")
    dst_dir.mkdir(parents=True)
    for name in ("bar.py", "foo.py", "meson.build", "__init__.py"):
        copy(src_dir / name, dst_dir)

    run_in_venv(venv, f"pip install {test_dir.parent}")
    run_in_venv(venv, "pip install meson-python meson ninja pytest")

    if backend_default == "pythran":
        run_in_venv(venv, "pip install pythran")

    install_command = "pip install . --no-build-isolation"
    if backend_default == "python":
        install_command += (
            " --config-settings=setup-args=-Dtransonic-backend=python"
        )

    run_in_venv(venv, install_command, cwd=tmpdir)
    run_in_venv(venv, "pytest tests", cwd=tmpdir)


@pytest.mark.skipif(nb_proc > 1, reason="No commandline in MPI")
@pytest.mark.xfail(backend_default == "cython", reason="Not yet implemented")
def test_meson_option(tmpdir, monkeypatch):
    """Only run `transonic --meson foo.py bar.py` in
    data_tests/package_for_test_meson/src/package_for_test_meson
    and compare with for_test__pythran__meson.build (same directory)
    """

    for name in ("bar.py", "foo.py", "meson.build"):
        copy(path_src_package / name, tmpdir)

    monkeypatch.chdir(tmpdir)

    argv = "transonic --meson bar.py foo.py".split()
    with patch.object(sys, "argv", argv):
        run()

    path_result = tmpdir / f"__{backend_default}__/meson.build"
    assert path_result.exists()

    saved_output_path = (
        path_src_package / f"for_test__{backend_default}__meson.build"
    )
    assert saved_output_path.exists()

    saved_meson_build = saved_output_path.read_text()
    produced_meson_build = path_result.read_text("utf8")

    assert saved_meson_build == produced_meson_build
