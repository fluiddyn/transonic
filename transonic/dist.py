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
from pathlib import Path
from distutils.sysconfig import get_config_var
from typing import Iterable
from concurrent.futures import ThreadPoolExecutor as Pool

from distutils.command.build_ext import build_ext as DistutilsBuildExt

try:
    from Cython.Distutils.build_ext import build_ext as CythonBuildExt
except ImportError:
    build_ext_classes = [DistutilsBuildExt]
    can_import_cython = False
else:
    build_ext_classes = [CythonBuildExt]
    can_import_cython = True

try:
    from pythran.dist import PythranBuildExt, PythranExtension
except ImportError:
    PythranBuildExt = object
    PythranExtension = object
    can_import_pythran = False
else:
    build_ext_classes.insert(0, PythranBuildExt)
    can_import_pythran = True

from .transpiler import make_backend_files
from .util import modification_date
from .compat import fspath

__all__ = [
    "make_backend_files",
    "PythranBuildExt",
    "PythranExtension",
    "can_import_pythran",
    "detect_pythran_extensions",
    "init_pythran_extensions",
    "get_logger",
    "ParallelBuildExt",
]


def get_logger(name):
    """Returns a logger instance using ``colorlog`` package if available; else
    defaults to ``logging`` standard library.

    """
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
    return logger


def detect_pythran_extensions(name_package: str,) -> Iterable[str]:
    """Recursively scans a package for Pythran extensions to build, and returns a
    list of strings, where each string is a module name. The package should be
    present in the current working directory.

    """
    if not can_import_pythran:
        return []
    ext_names = []
    if not os.path.exists(str(name_package)):
        raise FileNotFoundError(f"Check the name of the package: {name_package}")

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
                    fspath(path).replace(os.path.sep, ".").split(".py")[0]
                )
    return ext_names


def init_pythran_extensions(
    name_package: str,
    include_dirs: Iterable[str] = (),
    compile_args: Iterable[str] = (),
    exclude_exts: Iterable[str] = (),
    logger=None,
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
    if not modules or not can_import_pythran:
        return []

    if len(exclude_exts) > 0 and logger:
        logger.info(
            "Files in the packages " + str(exclude_exts) + " will not be built."
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

            pext = PythranExtension(mod, [py_file])
            pext.include_dirs.append(include_dirs)
            pext.extra_compile_args.extend(compile_args)
            extensions.append(pext)

    return extensions


class ParallelBuildExt(*build_ext_classes):
    @property
    def logger(self):
        try:
            import colorlog as logging
        except ImportError:
            import logging

        logger = logging.getLogger(self.logger_name)
        return logger

    def initialize_options(self):
        """Modify the following to packaging specific needs."""
        super().initialize_options()
        self.logger_name = "transonic"
        self.num_jobs_env_var = ""
        self.ignoreflags = ("-Wstrict-prototypes",)
        self.ignoreflags_startswith = ("-axMIC_", "-diag-disable:")

    def finalize_options(self):
        """Only changed to support setting ``self.parallel`` automatically."""
        if self.parallel is None:
            self.parallel = self.get_num_jobs()

        super().finalize_options()
        self.logger.debug(f"Parallel build enabled with {self.parallel} jobs")
        self.logger.debug(f"Base classes: {build_ext_classes}")

    def get_num_jobs(self):
        try:
            num_jobs = int(os.environ[self.num_jobs_env_var])
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
        self.check_extensions_list(self.extensions)

        for ext in self.extensions:
            try:
                # For Cython extensions
                ext.sources = self.cython_sources(ext.sources, ext)
            except AttributeError:
                pass

        # Invoke Distutils build_extensions method which respects
        # parallel building. Cython's build_ext ignores this
        DistutilsBuildExt.build_extensions(self)

    def _build_extensions_parallel(self):
        """A slightly modified version
        ``distutils.command.build_ext.build_ext._build_extensions_parallel``
        which:

        - filters out some problematic compiler flags
        - separates extensions of different types into different thread pools.

        """
        logger = self.logger
        self.compiler.compiler_so = [
            key
            for key in self.compiler.compiler_so
            if key not in self.ignoreflags
            and all([not key.startswith(s) for s in self.ignoreflags_startswith])
        ]

        # Set of all extension types
        ext_types = {type(ext) for ext in self.extensions}
        extensions_by_type = {T: [] for T in ext_types}
        for ext in self.extensions:
            extensions_by_type[ext.__class__].append(ext)

        def names(exts):
            return [ext.name for ext in exts]

        # Separate building extensions of different types to avoid race conditions
        num_jobs = self.parallel
        for exts in extensions_by_type.values():
            logger.info(f"Start build_extension: {names(exts)}")

            with Pool(num_jobs) as pool:
                pool.map(self.build_extension, exts)

            logger.info(f"Stop build_extension: {names(exts)}")
