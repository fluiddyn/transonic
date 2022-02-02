"""A pure Python module containing a few functions"""
import numpy as np


def twice(n: int):
    return 2 * n


def identity(n: int):
    return np.eye(twice(n) // 2)
