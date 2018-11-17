"""Utilities for the setup.py files
===================================

User API
--------

Provides the classes PythranBuildExt and PythranExtension to be used in the
setup.py.

.. autofunction:: detect_pythran_extensions

"""

import os
from pathlib import Path
from distutils.command.build_ext import build_ext

try:
    from pythran.dist import PythranBuildExt, PythranExtension

    can_import_pythran = True
except ImportError:
    can_import_pythran = False
    PythranBuildExt = build_ext
    PythranExtension = None

from .transpiler import make_pythran_files
from .util import modification_date

__all__ = [
    "make_pythran_files",
    "PythranBuildExt",
    "PythranExtension",
    "can_import_pythran",
    "detect_pythran_extensions",
    "modification_date",
]


def detect_pythran_extensions(name_package):

    if not can_import_pythran:
        return []
    ext_names = []
    for root, dirs, files in os.walk(name_package):
        path_dir = Path(root)
        for name in files:
            if (
                name.endswith("_pythran.py")
                or path_dir.name == "__pythran__"
                and name.endswith(".py")
            ):
                path = path_dir / name
                ext_names.append(
                    str(path).replace(os.path.sep, ".").split(".py")[0]
                )
    return ext_names
