import h5py
import numpy as np
from .for_test_exterior_import_jit_2 import func_import_2


const = 1
foo = 1


def func_import():
    return const + np.pi - np.pi + func_import_2()


def use_h5py():
    print("use_h5py")
