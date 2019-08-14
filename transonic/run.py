"""Command line transonic
============================

Internal API
------------

.. autofunction:: run

.. autofunction:: parse_args

"""

import argparse
from pathlib import Path
from glob import glob
import sys
from typing import Iterable, Optional
from warnings import warn

from transonic import __version__
from transonic.analyses import analyse_aot

from transonic.compiler import (
    compile_extensions,
    ext_suffix,
    wait_for_all_extensions,
)

from transonic.config import backend_default
from transonic.log import logger
from transonic.util import (
    has_to_build,
    clear_cached_extensions,
    can_import_accelerator,
)

doc = """
transonic: easily speedup your Python code with Pythran

"""


def run():
    """Run the transonic commandline

    See :code:`transonic -h`
    """
    args = parse_args()

    if args.version:
        print(__version__)
        return

    if not args.path and not args.clear_cache:
        logger.warning("No python files given. Nothing to do! ✨ 🍰 ✨.")
        return

    if args.clear_cache:
        clear_cached_extensions(args.clear_cache, force=args.force)
        return

    if args.verbose is None:
        logger.set_level(None)
    elif args.verbose == 1:
        logger.set_level("info")
    elif args.verbose > 1:
        logger.set_level("debug")
    logger.info(args)

    path = args.path

    if isinstance(path, list) and len(path) == 1:
        path = path[0]

    if isinstance(path, list):
        paths = path
    else:
        path = Path(path)
        if path.is_file():
            paths = (path,)
        elif path.is_dir():
            paths = path.glob("*.py")
        else:
            paths = glob(str(path))

    if not paths:
        logger.error(f"No input file found (args.path = {args.path})")
        sys.exit(1)

    from .backends import backends
    from transonic.config import backend_default

    make_backends_files(paths, backends[backend_default])

    if not can_import_accelerator() or args.no_pythran:
        return

    # find pythran files not already compiled
    backends_paths = {backend: [] for backend in backends}

    for path in paths:
        path = Path(path)
        backend_path = (
            path.parent / str("__" + backend_default + "__") / path.name
        )
        ext_path = backend_path.with_suffix(ext_suffix)
        if backend_path.exists() and has_to_build(ext_path, backend_path):
            backends_paths[backend_default].append(backend_path)

    compile_extensions(
        backends_paths[backend_default],
        backend_default,
        str_pythran_flags=args.pythran_flags,
        parallel=True,
        force=args.force,
    )

    if not args.no_blocking:
        wait_for_all_extensions()


def make_backends_files(
    paths_py,
    backend=None,
    force=False,
    log_level=None,
    mocked_modules: Optional[Iterable] = None,
):
    """Create backend files from a list of Python files"""

    if mocked_modules is not None:
        warn(
            "The argument mocked_modules is deprecated. "
            "It is now useless for Transonic.",
            DeprecationWarning,
        )

    if log_level is not None:
        logger.set_level(log_level)

    paths_out = []
    for path in paths_py:
        with open(path) as f:
            code = f.read()
        analyse = analyse_aot(code, path)
        path_out = backend.make_backend_file(path, analyse, force=force)
        if path_out:
            paths_out.append(path_out)

    if paths_out:
        nb_files = len(paths_out)
        if nb_files == 1:
            conjug = "s"
        else:
            conjug = ""

        logger.warning(
            f"{nb_files} files created or updated need{conjug}"
            f" to be {backend_default}ized"
        )

    return paths_out


def parse_args():
    """Parse the arguments"""
    parser = argparse.ArgumentParser(
        description=doc, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("path", help="Path file or directory.", nargs="*")

    parser.add_argument(
        "-f",
        "--force",
        help="write the file even if it is up-to-date",
        action="store_true",
    )

    parser.add_argument(
        "-V", "--version", help="print version and exit", action="store_true"
    )

    parser.add_argument("-v", "--verbose", help="verbose mode", action="count")

    parser.add_argument(
        "-np",
        "--no-pythran",
        help="do not compile the Pythran files with Pythran",
        action="store_true",
    )

    parser.add_argument(
        "-nb",
        "--no-blocking",
        help="launch the compilation in the background and return",
        action="store_true",
    )

    parser.add_argument(
        "-pf",
        "--pythran-flags",
        help=(
            "Flags sent to Pythran. "
            'Default is "-march=native -DUSE_XSIMD". '
            "There has to be atleast one space in the passed string! "
            'Example: transonic foo.py -pf "-march=native "\n'
        ),
        type=str,
        default="",
    )

    parser.add_argument(
        "-cc",
        "--clear-cache",
        help=("clear the cached extensions for a module"),
        type=str,
        # default="",
    )

    return parser.parse_args()


if __name__ == "__main__":
    run()
