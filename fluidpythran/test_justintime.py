import sys
import os

import numpy as np

try:
    import pythran
except ImportError:
    pythran = None

from .justintime import path_cachedjit, modules
from .pythranizer import scheduler, wait_for_all_extensions
from . import mpi

scheduler.nb_cpus = 2

module_name = "fluidpythran.for_test_justintime"

path_pythran_dir = mpi.PathSeq(path_cachedjit) / module_name.replace(
    ".", os.path.sep
)


def delete_pythran_files(func_name):
    for path_pythran_file in path_pythran_dir.glob(func_name + "*"):
        if path_pythran_file.exists():
            path_pythran_file.unlink()


if mpi.rank == 0:
    delete_pythran_files("func1")
    delete_pythran_files("func2")
    delete_pythran_files("func_dict")

mpi.barrier()


def test_cachedjit():

    from time import sleep
    from .for_test_justintime import func1

    a = np.arange(2)
    b = [1, 2]

    for _ in range(2):
        func1(a, b)
        sleep(0.1)


def test_cachedjit_simple():

    from time import sleep
    from .for_test_justintime import func2

    func2(1)

    if not pythran:
        return

    mod = modules[module_name]
    cjit = mod.cachedjit_functions["func2"]

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


def test_cachedjit_dict():
    from time import sleep
    from .for_test_justintime import func_dict

    d = dict(a=1, b=2)
    func_dict(d)

    if not pythran:
        return

    mod = modules[module_name]
    cjit = mod.cachedjit_functions["func_dict"]

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
