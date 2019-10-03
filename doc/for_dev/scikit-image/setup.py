import os
import sys
from distutils.core import setup
from pathlib import Path

import numpy as np

from transonic.dist import make_backend_files, init_transonic_extensions

path_here = Path(__file__).parent.absolute()
include_dirs = [np.get_include()]

pack_name = "future"

paths = tuple((path_here / pack_name).glob("*.py"))

for backend in ("pythran", "cython", "numba"):
    make_backend_files(paths, backend=backend)

extensions = []
if "egg_info" not in sys.argv:
    # compile_arch = os.getenv("CARCH", "native")
    extensions = init_transonic_extensions(
        pack_name,
        backend="pythran",
        include_dirs=[np.get_include()],
        # compile_args=("-O3", f"-march={compile_arch}", "-DUSE_XSIMD"),
        inplace=True,
    )
    extensions.extend(
        init_transonic_extensions(pack_name, backend="cython", inplace=True)
    )
    init_transonic_extensions(pack_name, backend="numba")


setup(
    name=pack_name,
    ext_modules=extensions,
    # script_name="setup.py",
    script_args=["build_ext", "--inplace"],
    # cmdclass=dict(build_ext=ParallelBuildExt),
)
