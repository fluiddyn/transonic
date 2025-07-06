import os
import sys
from pathlib import Path

import nox
from packaging import version

os.environ.update({"PDM_IGNORE_SAVED_PYTHON": "1"})
nox.options.reuse_existing_virtualenvs = True


@nox.parametrize("with_cython", [0, 1])
@nox.parametrize("with_pythran", [0, 1])
@nox.session
def test(session, with_pythran, with_cython):

    env_pdm_install = os.environ.copy()
    env_pdm_install["CFLAGS"] = "-O2"

    command = "pdm sync -G base-test"
    session.run_install(*command.split(), external=True, env=env_pdm_install)

    py_version = (
        session.python
        if session.python is not None
        else sys.version.split(maxsplit=1)[0]
    )
    if version.parse(py_version) < version.parse("3.13"):
        # Numba not yet compatible with 3.13 (2024-12-02)
        session.install("numba")

    session.install("jax", "jaxlib")

    if with_pythran:
        session.install("pythran")
    if with_cython:
        session.install("cython")

    if version.parse(py_version) < version.parse("3.12"):
        session.install("setuptools<60.0")
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

    backends = ["python", "pythran", "numba", "jax", "cython"]

    # potentially remove jax if broken (happens randomly in CI)
    out = session.run("python", ".check_jax.py", silent=True)
    if out.strip() != "jax usable":
        backends.remove("jax")

    for backend in backends:
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
    session.run_install("pdm", "sync", "-G", "doc", external=True)
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
