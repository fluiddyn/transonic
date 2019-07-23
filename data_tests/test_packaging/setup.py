from distutils.core import setup, Extension
from pathlib import Path
import numpy as np
from transonic.dist import (
    make_backend_files,
    init_transonic_extensions,
    ParallelBuildExt,
)

path_sources = Path(__file__).parent.absolute()
include_dirs = [np.get_include()]

try:
    from Cython.Build import cythonize
except ImportError:
    # from setuptools import Extension
    extensions = [
        Extension(
            "add_cython",
            include_dirs=[str(path_sources)] + include_dirs,
            libraries=["m"],
            library_dirs=[],
            sources=[str(path_sources / "add_cython.c")],
        )
    ]
    print(extensions)
else:
    extensions = cythonize(
        Extension("add_cython", ["add_cython.pyx"], include_dirs=include_dirs)
    )

make_backend_files([path_sources / "add.py"])
extensions.extend(init_transonic_extensions(".", include_dirs=include_dirs))

setup(
    name="add",
    ext_modules=extensions,
    script_name="setup.py",
    script_args=["build_ext"],
    cmdclass=dict(build_ext=ParallelBuildExt),
)
