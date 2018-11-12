import sys

import numpy as np

try:
    import pythran
except ImportError:
    pythran = None


from .cached_jit import path_cachedjit, modules

module_name = "fluidpythran.for_test_cached_jit"

path_pythran_dir = path_cachedjit / module_name.replace(".", "__")


def delete_pythran_files(func_name):
    for path_pythran_file in path_pythran_dir.glob(func_name + ".*"):
        if path_pythran_file.exists():
            path_pythran_file.unlink()


delete_pythran_files("func1")
delete_pythran_files("func2")


def test_cachedjit():

    from time import sleep
    from .for_test_cached_jit import func1

    a = b = np.arange(2)

    for _ in range(2):
        func1(a, b)
        sleep(0.1)


def test_cachedjit_simple():

    from time import sleep
    from .for_test_cached_jit import func2

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

    from .for_test_cached_jit import func2

    func2(1)
