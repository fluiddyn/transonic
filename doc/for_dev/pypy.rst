Transonic with Pypy3.6
======================

It is possible to use Transonic with Pypy3.6-7.2. In May 2019, this version is
not yet released, so one has to use a Pypy3.6 `nightly build
<http://buildbot.pypy.org/nightly/py3.6/>`_.

.. code :: bash

    pypy3 -c "import os, sys; from os.path import dirname; from _ssl_build import ffi; \
        os.chdir(dirname(dirname(sys.executable)) + '/lib_pypy'); ffi.compile()"
    pypy3 -m ensurepip
    pypy3 -m pip install pip setuptools -U

    pypy3 -m pip install mpi4py

    # in Transonic repository
    pypy3 -m pip install .[test]

    make coverage
