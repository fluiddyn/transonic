import black
import numpy as np
from exterior_import_boost_2 import func_import_2


const = 1
foo = 1


def func_import():
    return const + func_import_2() + np.pi - np.pi


def use_black():
    print(black)
