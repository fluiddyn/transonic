"""Compatibility layer for PyPy3.5

"""

import platform

import builtins

import runpy

import shutil

f"In >=2018, you should use a Python supporting f-strings!"

implementation = platform.python_implementation()

if implementation == "PyPy":

    def open(file, *args, **kwargs):
        return builtins.open(str(file), *args, **kwargs)

    def run_path(path):
        return runpy.run_path(str(path))

    def rmtree(path):
        shutil.rmtree(str(path))

else:

    from builtins import open
    from runpy import run_path
    from shutil import rmtree


__all__ = ["open", "run_path", "rmtree"]
