from distutils.core import setup, Extension
from pathlib import Path

import numpy as np
from Cython.Build import cythonize

path_here = Path(__file__).parent.absolute()
include_dirs = [np.get_include()]

pyx_files = (path_here / "pyx").glob("*.pyx")
extensions = []
for pyx_file in pyx_files:
    name = pyx_file.name.split(".", 1)[0]
    extensions.append(
        Extension("pyx." + name, [str(pyx_file)], include_dirs=include_dirs)
    )

extensions = cythonize(extensions, language_level=3)

setup(
    name="pyx",
    ext_modules=extensions,
    script_args=["build_ext", "--inplace"],
)
