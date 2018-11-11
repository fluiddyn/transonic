
import numpy as np

from .cachedjit import path_cachedjit

path_pythran_dir = path_cachedjit / "fluidpythran__for_test_cachedjit"


def delete_pythran_files(func_name):
    for path_pythran_file in path_pythran_dir.glob(func_name + ".*"):
        if path_pythran_file.exists():
            path_pythran_file.unlink()


delete_pythran_files("func1")
delete_pythran_files("func2")

from .for_test_cachedjit import func1, func2


def test_cachedjit():

    from time import sleep

    a = b = np.arange(2)

    for _ in range(2):
        func1(a, b)
        sleep(0.1)


def test_cachedjit_simple():

    from time import sleep

    for _ in range(10):
        func2(1)
        sleep(1)
