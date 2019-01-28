"""Utilities for the setup.py files
===================================

User API
--------

Provides the classes PythranBuildExt and PythranExtension to be used in the
setup.py.

.. autofunction:: detect_pythran_extensions

"""

import os
import sys
from datetime import datetime
from pathlib import Path
from distutils.command.build_ext import build_ext
from distutils.sysconfig import get_config_var
from logging import ERROR, INFO
from typing import Iterable
from concurrent.futures import ThreadPoolExecutor as Pool

try:
    from pythran.dist import PythranBuildExt, PythranExtension

    can_import_pythran = True
except ImportError:
    can_import_pythran = False
    PythranBuildExt = build_ext
    PythranExtension = object

from .transpiler import make_backend_files
from .util import modification_date

__all__ = [
    "make_backend_files",
    "PythranBuildExt",
    "PythranExtension",
    "can_import_pythran",
    "detect_pythran_extensions",
    "init_pythran_extensions",
    "init_logger",
    "ParallelBuildExt"
]


def init_logger(name):
    """Returns a logger instance using ``colorlog`` package if available; else
    defaults to ``logging`` standard library.

    """
    if "egg_info" in sys.argv:
        level = ERROR
    else:
        level = INFO

    try:
        import colorlog as logging

        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.ColoredFormatter("%(log_color)s%(levelname)s: %(message)s")
        )
    except ImportError:
        import logging

        handler = logging.StreamHandler()

    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger


def detect_pythran_extensions(
    name_package: str,
) -> Iterable[str]:
    """Recursively scans a package for Pythran extensions to build, and returns a
    list of strings, where each string is a module name. The package should be
    present in the current working directory.

    """
    if not can_import_pythran:
        return []
    ext_names = []
    for root, dirs, files in os.walk(str(name_package)):
        path_dir = Path(root)
        for name in files:
            if (
                name.endswith("_pythran.py")
                or path_dir.name == "__pythran__"
                and name.endswith(".py")
            ):
                path = path_dir / name
                ext_names.append(
                    os.fspath(path).replace(os.path.sep, ".").split(".py")[0]
                )
    return ext_names


def modification_date(filename) -> datetime:
    """Get modification date of a file."""
    t = os.path.getmtime(filename)
    return datetime.fromtimestamp(t)


def init_pythran_extensions(
    name_package: str,
    include_dirs: Iterable[str] = (),
    compile_args: Iterable[str] = (),
    exclude_exts: Iterable[str] = (),
    logger=None
):
    """Detects pythran extensions under a package and returns a list of
    Extension instances ready to be passed into the ``setup()`` function.

    Parameters
    ----------
    name_package:

        Package to be recursively scanned for Pythran extensions.

    include_dirs:

        Directories to include while building extensions, for e.g.:
        ``numpy.get_include()``

    compile_args:

        Arguments to be used while compiling extensions

    exclude_ext:

        Extensions to be excluded from the detected list.

    """
    modules = detect_pythran_extensions(name_package)
    if not modules:
        return []

    if len(exclude_exts) > 0 and logger:
        logger.info(
            "Files in the packages "
            + str(exclude_exts)
            + " will not be built."
        )
    develop = "develop" in sys.argv

    extensions = []
    for mod in modules:
        package = mod.rsplit(".", 1)[0]
        if any(package == excluded for excluded in exclude_exts):
            continue
        base_file = mod.replace(".", os.path.sep)
        py_file = base_file + ".py"
        suffix = get_config_var("EXT_SUFFIX")
        bin_file = base_file + suffix
        if (
            not develop
            or not os.path.exists(bin_file)
            or modification_date(bin_file) < modification_date(py_file)
        ):

            if logger:
                logger.info(
                    "Extension has to be built: {} -> {} ".format(
                        py_file, os.path.basename(bin_file)
                    )
                )

            pext = PythranExtension(
                mod,
                [py_file],
            )
            pext.include_dirs.append(include_dirs)
            pext.extra_compile_args.extend(compile_args)
            extensions.append(pext)

    return extensions


class ParallelBuildExt(build_ext, PythranBuildExt):
    # Modify the following to packaging specific needs
    PARALLEL = True
    LOGGER_NAME = "transonic"
    NUM_JOBS_ENV_VAR = ""
    ignoreflags = ("-Wstrict-prototypes",)
    ignoreflags_startswith = ("-axMIC_", "-diag-disable:")

    @property
    def logger(self):
        try:
            import colorlog as logging
        except ImportError:
            import logging

        return logging.getLogger(self.LOGGER_NAME)

    @property
    def num_jobs(self):
        try:
            num_jobs = int(os.environ[self.NUM_JOBS_ENV_VAR])
        except KeyError:
            import multiprocessing
            num_jobs = multiprocessing.cpu_count()

            try:
                from psutil import virtual_memory
            except ImportError:
                pass
            else:
                avail_memory_in_Go = virtual_memory().available / 1e9
                limit_num_jobs = round(avail_memory_in_Go / 3)
                num_jobs = min(num_jobs, limit_num_jobs)
        return num_jobs

    def build_extensions(self):
        """Parallelize
        ``distutils.command.build_ext.build_ext.build_extensions`` using threads.

        """
        self.compiler.compiler_so = [
            key
            for key in self.compiler.compiler_so
            if key not in self.ignoreflags
            and all([not key.startswith(s) for s in self.ignoreflags_startwith])
        ]

        if not self.PARALLEL:
            return super().build_extensions()

        self.check_extensions_list(self.extensions)

        for ext in self.extensions:
            try:
                # For Cython extensions
                ext.sources = self.cython_sources(ext.sources, ext)
            except AttributeError:
                pass

        pythran_extensions = []
        other_extensions = []
        for ext in self.extensions:
            if isinstance(ext, PythranExtension):
                pythran_extensions.append(ext)
            else:
                other_extensions.append(ext)

        def names(exts):
            return [ext.name for ext in exts]

        # Separate building pythran and other extensions to avoid race condtions
        with Pool(self.num_jobs) as pool:
            self.logger.info(
                f"Start build_extension: {names(pythran_extensions)}"
            )
            pool.map(self.build_extension, pythran_extensions)

        self.logger.info(f"Stop build_extension: {names(pythran_extensions)}")

        with Pool(self.num_jobs) as pool:
            self.logger.info(
                f"Start build_extension: {names(other_extensions)}"
            )
            pool.map(self.build_extension, other_extensions)

        self.logger.info(f"Stop build_extension: {names(other_extensions)}")
