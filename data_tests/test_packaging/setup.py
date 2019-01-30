from distutils.core import setup, Extension
from Cython.Build import cythonize
import numpy as np
from transonic.dist import init_pythran_extensions, ParallelBuildExt


include_dirs = [np.get_include()]

extensions = cythonize(
    Extension("add_cython", ['add_cython.pyx'], include_dirs=include_dirs)
)

extensions.extend(
    init_pythran_extensions(".", include_dirs=include_dirs)
)

setup(
    name="add",
    ext_modules=cythonize(extensions),
    script_name='setup.py',
    script_args=['build_ext'],
    cmdclass=dict(build_ext=ParallelBuildExt),
)
