Transonic with Pypy3.6
======================

It is possible to use Transonic with Pypy3.6-7.2.

.. code :: bash

    pypy3 -c "import os, sys; from os.path import dirname; from _ssl_build import ffi; \
        os.chdir(dirname(dirname(sys.executable)) + '/lib_pypy'); ffi.compile()"
    pypy3 -m ensurepip
    pypy3 -m pip install pip setuptools -U

    pypy3 -m pip install mpi4py

    # in Transonic repository
    pypy3 -m pip install .[test]

    make coverage
