import os
import sys
from packaging import version

import nox

os.environ.update({"PDM_IGNORE_SAVED_PYTHON": "1"})


def _test(session):
    session.run("make", "tests_ipynb", external=True)
    session.run("make", "tests_coverage", external=True)


def _install_base(session):
    command = "pdm install -G base_test"
    session.run_always(*command.split(), external=True)

    py_version = session.python if session.python is not None else sys.version.split(maxsplit=1)[0]
    if version.parse(py_version) < version.parse("3.12"):
        session.run_always("pip", "install", "numba")


@nox.session
def test_without_pythran(session):
    _install_base(session)
    _test(session)


@nox.session
def test_with_pythran(session):
    _install_base(session)
    session.install("pythran")
    _test(session)


@nox.session
def test_with_cython(session):
    _install_base(session)
    session.install("cython")
    _test(session)


@nox.session
def test_with_pythran_cython(session):
    _install_base(session)
    session.install("pythran", "cython")
    _test(session)
