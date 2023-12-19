"""Utilities for the setup.py files
===================================

User API
--------

Provides the classes PythranBuildExt and PythranExtension to be used in the
setup.py.

.. autofunction:: detect_transonic_extensions

.. autofunction:: init_transonic_extensions

"""

import os
import sys
from pathlib import Path
from sysconfig import get_config_var
from typing import Iterable
from concurrent.futures import ThreadPoolExecutor as Pool
import re

from setuptools.command.build_ext import build_ext as SetuptoolsBuildExt

try:
    from Cython.Distutils.build_ext import build_ext as CythonBuildExt
    from Cython.Build import cythonize
except ImportError:
    build_ext_classes = [SetuptoolsBuildExt]
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

from transonic.util import modification_date
from transonic.config import backend_default
from transonic.backends import make_backend_files, backends
from transonic.util import can_import_accelerator
from transonic.log import get_logger

__all__ = [
    "PythranBuildExt",
    "PythranExtension",
    "can_import_pythran",
    "detect_transonic_extensions",
    "init_pythran_extensions",
    "init_transonic_extensions",
    "get_logger",
    "ParallelBuildExt",
    "make_backend_files",
]


def detect_transonic_extensions(
    name_package: str, backend: str = backend_default
) -> Iterable[str]:
    """Recursively scans a package for Pythran extensions to build, and returns a
    list of strings, where each string is a module name. The package should be
    present in the current working directory.

    """
    if backend != "numba" and not can_import_accelerator(backend):
        return []
    ext_names = []
    if not os.path.exists(str(name_package)):
        raise FileNotFoundError(f"Check the name of the package: {name_package}")

    backend = backends[backend]
    if backend.suffix_extension == ".py":
        # we have to filter out the "extensions"
        pattern = re.compile("_[a-f0-9]{32}.py$")

    extension = ".py"
    for root, dirs, files in os.walk(str(name_package)):
        path_dir = Path(root)
        for name in files:
            if (
                path_dir.name == f"__{backend.name}__"
                and name.endswith(extension)
                and not name.startswith("__ext__")
            ):
                path = path_dir / name
                if (
                    backend.suffix_extension == ".py"
                    and pattern.search(name) is not None
                ):
                    continue
                ext_names.append(
                    str(path).replace(os.path.sep, ".").split(extension)[0]
                )

    return ext_names


def init_pythran_extensions(
    name_package: str,
    include_dirs: Iterable[str] = (),
    compile_args: Iterable[str] = (),
    exclude_exts: Iterable[str] = (),
    logger=None,
):
    return init_transonic_extensions(
        name_package, "pythran", include_dirs, compile_args, exclude_exts, logger
    )


def init_transonic_extensions(
    name_package: str,
    backend: str = backend_default,
    include_dirs: Iterable[str] = (),
    compile_args: Iterable[str] = (),
    exclude_exts: Iterable[str] = (),
    logger=None,
    inplace=None,
    annotate=False,
):
    """Detects pythran extensions under a package and returns a list of
    Extension instances ready to be passed into the ``setup()`` function.

    Parameters
    ----------
    name_package:

        Package to be recursively scanned for Pythran extensions.

    backend : str

        Only initialize extensions for this backend. If None, initialize
        extensions for the default backend (set by an environment variable).

    include_dirs:

        Directories to include while building extensions, for e.g.:
        ``numpy.get_include()``

    compile_args:

        Arguments to be used while compiling extensions

    exclude_ext:

        Extensions to be excluded from the detected list.

    """
    modules = detect_transonic_extensions(name_package, backend)
    if not modules:
        return []

    if backend == "numba":
        # very special case for Numba
        paths = [Path(mod.replace(".", os.path.sep) + ".py") for mod in modules]
        backends["numba"].compile_extensions(paths, None)
        return []
    elif backend == "pythran":
        try:
            from pythran.dist import PythranExtension
        except ImportError as err:
            raise RuntimeError(
                f"backend = {backend} but Pythran is not importable. "
                f"(sys.argv = {sys.argv})"
            ) from err

        BackendExtension = PythranExtension
    elif backend == "cython":

        def BackendExtension(mod, files):
            # to avoid a bug: Cython does not take into account .pxd file
            ext = cythonize(files[0], annotate=annotate, language_level=3)[0]
            ext.name = mod
            return ext

    else:
        return []

    if len(exclude_exts) > 0 and logger:
        logger.info(
            "Files in the packages " + str(exclude_exts) + " will not be built."
        )

    if inplace is None:
        inplace = "develop" in sys.argv or (
            "build_ext" in sys.argv and "--inplace" in sys.argv
        )

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
            not inplace
            or not os.path.exists(bin_file)
            or modification_date(bin_file) < modification_date(py_file)
        ):
            if logger:
                logger.info(
                    "Extension has to be built: {} -> {} ".format(
                        py_file, os.path.basename(bin_file)
                    )
                )

            pext = BackendExtension(mod, [py_file])
            if isinstance(include_dirs, str):
                include_dirs = [include_dirs]
            pext.include_dirs.extend(include_dirs)
            pext.extra_compile_args.extend(compile_args)
            extensions.append(pext)

    return extensions


class ParallelBuildExt(*build_ext_classes):
    @property
    def logger(self):
        logger = get_logger(self.logger_name)
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
                self.logger.warning(
                    "psutil not available at build time. "
                    "Cannot check memory available and potentially limit num_jobs."
                )
            else:
                avail_memory_in_Go = virtual_memory().available / 1e9
                limit_num_jobs = max(1, round(avail_memory_in_Go / 3))
                if num_jobs > limit_num_jobs:
                    self.logger.info(
                        f"num_jobs limited by memory, fixed at {limit_num_jobs}"
                    )
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
        SetuptoolsBuildExt.build_extensions(self)

    def _build_extensions_parallel(self):
        """A slightly modified version
        ``setuptools.command.build_ext.build_ext._build_extensions_parallel``
        which:

        - filters out some problematic compiler flags
        - separates extensions of different types into different thread pools.

        """
        logger = self.logger
        if hasattr(self.compiler, "compiler_so"):
            self.compiler.compiler_so = [
                key
                for key in self.compiler.compiler_so
                if key not in self.ignoreflags
                and all(
                    [not key.startswith(s) for s in self.ignoreflags_startswith]
                )
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
        logger.info(f"_build_extensions_parallel with num_jobs = {num_jobs}")
        for type_ext, exts in extensions_by_type.items():
            logger.info(f"Building extensions of type {type_ext}: {names(exts)}")

            with Pool(num_jobs) as pool:
                pool.map(self.build_extension, exts)

            logger.info(f"Extensions built: {names(exts)}")
