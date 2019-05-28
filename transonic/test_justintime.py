import sys
import os
from time import sleep
from shutil import rmtree

import numpy as np

try:
    import pythran
except ImportError:
    pythran = None

from .util import path_jit_classes
from .justintime import path_jit, modules
from .pythranizer import scheduler, wait_for_all_extensions
from . import mpi

scheduler.nb_cpus = 2

module_name = "transonic.for_test_justintime"

str_relative_path = module_name.replace(".", os.path.sep)

path_jit = mpi.PathSeq(path_jit)

path_pythran_dir = path_jit / str_relative_path
path_classes_dir = path_jit_classes / str_relative_path
path_classes_dir1 = path_jit / path_jit_classes.name / str_relative_path


def delete_pythran_files(func_name):
    for path_pythran_file in path_pythran_dir.glob(func_name + "*"):
        if path_pythran_file.exists():
            path_pythran_file.unlink()


if mpi.rank == 0:
    delete_pythran_files("func1")
    delete_pythran_files("func2")
    delete_pythran_files("func_dict")
    delete_pythran_files("fib")
    delete_pythran_files("use_fib")

    if path_classes_dir.exists():
        rmtree(path_classes_dir)
    if path_classes_dir1.exists():
        rmtree(path_classes_dir1)

mpi.barrier()


def test_jit():

    from .for_test_justintime import func1

    a = np.arange(2)
    b = [1, 2]

    for _ in range(2):
        func1(a, b)
        sleep(0.1)


def fib():
    from .for_test_justintime import fib, use_fib

    fib2 = fib(2)
    result = use_fib()
    wait_for_all_extensions()
    assert fib2 == fib(2)
    assert result == use_fib()


def test_jit_simple():

    from .for_test_justintime import func2

    func2(1)

    if not pythran:
        return

    mod = modules[module_name]
    cjit = mod.jit_functions["func2"]

    for _ in range(100):
        func2(1)
        sleep(0.1)
        if not cjit.compiling:
            sleep(0.1)
            func2(1)
            break

    del sys.modules[module_name]
    del modules[module_name]

    from .for_test_justintime import func2

    func2(1)


def test_jit_dict():
    from .for_test_justintime import func_dict

    d = dict(a=1, b=2)
    func_dict(d)

    if not pythran:
        return

    mod = modules[module_name]
    cjit = mod.jit_functions["func_dict"]

    d = dict(a=1, b=2)
    func_dict(d)

    wait_for_all_extensions()

    for _ in range(100):
        d = dict(a=1, b=2)
        func_dict(d)
        sleep(0.1)
        if not cjit.compiling:
            sleep(0.1)
            func_dict(d)
            break


def test_jit_method():
    from .for_test_justintime import MyClass

    obj = MyClass()
    obj.check()

    if not pythran:
        return

    obj = MyClass()
    obj.check()

    wait_for_all_extensions()

    obj.check()
