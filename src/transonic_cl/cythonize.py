import sys
from distutils.core import setup

from Cython.Build import cythonize
import numpy as np

path = sys.argv.pop()
sys.argv.extend(("build_ext", "--inplace"))

setup(
    ext_modules=cythonize(path, language_level=3), include_dirs=[np.get_include()]
)
