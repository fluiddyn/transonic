import os
import sys
from packaging import version
from pathlib import Path

import nox

os.environ.update({"PDM_IGNORE_SAVED_PYTHON": "1"})
nox.options.reuse_existing_virtualenvs = 1


@nox.parametrize("with_cython", [0, 1])
@nox.parametrize("with_pythran", [0, 1])
@nox.session
def test(session, with_pythran, with_cython):
    command = "pdm sync -G base_test"
    session.run_always(*command.split(), external=True)

    py_version = (
        session.python
        if session.python is not None
        else sys.version.split(maxsplit=1)[0]
    )
    if version.parse(py_version) < version.parse("3.12"):
        session.install("numba")
    else:
        session.install("setuptools")

    if with_pythran:
        session.install("pythran")
    if with_cython:
        session.install("cython")

    if version.parse(py_version) < version.parse("3.12"):
        for backend in ("python", "pythran"):
            print(f"TRANSONIC_BACKEND={backend}")
            session.run(
                "pytest",
                "--nbval-lax",
                "data_tests/ipynb",
                env={"TRANSONIC_BACKEND": backend},
            )

    path_coverage = Path(".coverage")
    path_coverage.mkdir(exist_ok=True)

    code_dependencies = 10 * with_pythran + with_cython

    for backend in ("python", "pythran", "numba", "cython"):
        print(f"TRANSONIC_BACKEND={backend}")
        session.run(
            "pytest",
            "--cov",
            "--cov-config=pyproject.toml",
            "tests",
            env={
                "COVERAGE_FILE": f".coverage/coverage{code_dependencies}.{backend}",
                "TRANSONIC_BACKEND": backend,
            },
        )

    command = "mpirun -np 2 coverage run --rcfile=pyproject.toml -m mpi4py -m pytest tests"
    session.run(
        *command.split(),
        external=True,
        env={
            "TRANSONIC_BACKEND": "pythran",
        },
    )


@nox.session
def doc(session):
    session.run_always("pdm", "sync", "-G", "doc", external=True)
    session.chdir("doc")
    session.run("make", "cleanall", external=True)
    session.run("make", external=True)
