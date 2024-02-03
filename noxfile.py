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


def _get_version_from_pyproject(path=Path.cwd()):
    if isinstance(path, str):
        path = Path(path)

    if not path.name == "pyproject.toml":
        path /= "pyproject.toml"

    in_project = False
    version = None
    with open(path, encoding="utf-8") as file:
        for line in file:
            if line.startswith("[project]"):
                in_project = True
            if line.startswith("version =") and in_project:
                version = line.split("=")[1].strip()
                version = version[1:-1]
                break

    assert version is not None
    return version


@nox.session(name="add-tag-for-release", venv_backend="none")
def add_tag_for_release(session):
    session.run("hg", "pull", external=True)

    result = session.run(
        *"hg log -r default -G".split(), external=True, silent=True
    )
    if result[0] != "@":
        session.run("hg", "update", "default", external=True)

    version = _get_version_from_pyproject()
    print(f"{version = }")

    result = session.run("hg", "tags", "-T", "{tag},", external=True, silent=True)
    last_tag = result.split(",", 2)[1]
    print(f"{last_tag = }")

    if last_tag == version:
        session.error("last_tag == version")

    answer = input(
        f'Do you really want to add and push the new tag "{version}"? (yes/[no]) '
    )

    if answer != "yes":
        print("Maybe next time then. Bye!")
        return

    print("Let's go!")
    session.run("hg", "tag", version, external=True)
    session.run("hg", "push", external=True)
