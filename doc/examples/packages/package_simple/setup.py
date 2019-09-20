"""
No pyproject.toml file because in some cases, isolated build cannot be used.

"""
import sys
import os
from pathlib import Path

from runpy import run_path

from setuptools.dist import Distribution
from setuptools import setup, find_packages

if sys.version_info[:2] < (3, 6):
    raise RuntimeError("Python version >= 3.6 required.")


def install_setup_requires():
    dist = Distribution()
    # Honor setup.cfg's options.
    dist.parse_config_files(ignore_option_errors=True)
    if dist.setup_requires:
        dist.fetch_build_eggs(dist.setup_requires)


install_setup_requires()

from transonic.dist import make_backend_files, init_transonic_extensions
import numpy as np

here = Path(__file__).parent.absolute()

pack_name = "package_simple"
pack_dir = here / pack_name

# Get the version from the relevant file
version = run_path(pack_name + "/_version.py")
__version__ = version["__version__"]

install_requires = ["transonic", "numpy", "matplotlib"]

relative_paths = ["util.py", "calcul.py"]
make_backend_files([pack_dir / path for path in relative_paths])

extensions = []
if "egg_info" not in sys.argv:
    compile_arch = os.getenv("CARCH", "native")
    extensions = init_transonic_extensions(
        pack_name,
        include_dirs=[np.get_include()],
        compile_args=("-O3", f"-march={compile_arch}", "-DUSE_XSIMD"),
    )

setup(
    version=__version__,
    packages=find_packages(exclude=["doc"]),
    install_requires=install_requires,
    ext_modules=extensions,
)
