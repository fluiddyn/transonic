import h5py
import numpy as np
from .exterior_import_jit_2 import func_import_2


const = 1
foo = 1


def func_import():
    return const + func_import_2() + np.pi - np.pi


def use_h5py():
    print("use_h5py")
