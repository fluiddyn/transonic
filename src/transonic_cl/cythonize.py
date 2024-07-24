import sys
from setuptools import setup

import numpy as np
from Cython.Build import cythonize

path = sys.argv.pop()
sys.argv.extend(("build_ext", "--inplace"))

setup(
    ext_modules=cythonize(path, language_level=3), include_dirs=[np.get_include()]
)
