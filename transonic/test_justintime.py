import sys
import os
from time import sleep
from shutil import rmtree

import numpy as np

from transonic.compiler import scheduler, wait_for_all_extensions
from transonic.justintime import path_jit, modules
from transonic import mpi
from transonic.util import path_jit_classes, can_import_accelerator

scheduler.nb_cpus = 2

module_name = "transonic.for_test_justintime"

str_relative_path = module_name.replace(".", os.path.sep)

path_jit = mpi.PathSeq(path_jit)

path_jit_dir = path_jit / str_relative_path
path_classes_dir = path_jit_classes / str_relative_path
path_classes_dir1 = path_jit / path_jit_classes.name / str_relative_path

if mpi.rank == 0:
    if path_jit.exists():
        rmtree(path_jit_dir, ignore_errors=True)
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


def test_fib():
    from .for_test_justintime import fib, use_fib

    fib2 = fib(2)
    result = use_fib()
    wait_for_all_extensions()
    assert fib2 == fib(2)
    assert result == use_fib()


def test_jit_simple():

    from .for_test_justintime import func2

    func2(1)

    if not can_import_accelerator():
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

    if not can_import_accelerator():
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

    if not can_import_accelerator():
        return

    obj = MyClass()
    obj.check()

    wait_for_all_extensions()

    obj.check()


def test_jit_method2():
    from .for_test_justintime import MyClass2

    obj = MyClass2()
    obj.check()

    if not can_import_accelerator():
        return

    obj = MyClass2()
    obj.check()

    wait_for_all_extensions()

    obj.check()


def test_func0():
    from .for_test_justintime import func0, func0_jitted

    func02 = func0(2.1)
    result = func0_jitted(2.1)
    wait_for_all_extensions()
    assert func02 == func0(2.1)
    assert result == func0(2.1)


# jitted function that uses a local function, a jitted local function
# and a jitted imported function (with a different name)
def test_main():
    from .for_test_justintime import main

    main_res = main(2)
    wait_for_all_extensions()
    assert main_res == 5


def test_jit_imported():
    from .for_test_justintime import jitted_func_import, func_import

    result = jitted_func_import()
    wait_for_all_extensions()
    assert result == jitted_func_import() == func_import()
